import asyncio
import json
import logging
import os
import sys
from typing import Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse
from jsonrpc import JSONRPCResponseManager, dispatcher

from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types
import mcp.types as mcp_types

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent import FlightAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk_server")

# Global State
mcp_session: Optional[ClientSession] = None
flight_agent: Optional[FlightAgent] = None
runner: Optional[Runner] = None
# Queues for broadcasting
chat_queue = asyncio.Queue()
a2ui_queue = asyncio.Queue()

# Helper to manage global MCP connection
class ADKClientSession(ClientSession):
    async def _received_notification(self, notification: mcp_types.ServerNotification) -> None:
        # Intercept resource updates
        logger.info(f"Received Notification: {notification}")
        if notification.method == "notifications/resources/updated":
             uri = notification.params.uri
             logger.info(f"Resource Updated: {uri}, fetching new content...")
             try:
                # We need to spawn a task because we can't block the read loop?
                # Actually _received_notification is awaited in the read loop.
                # read_resource sends a request and waits for response.
                # If we do it HERE, we might deadlock if read_resource needs the read loop to process response?
                # YES. If _received_notification is called by the read loop, and we call read_resource which waits for a response provided by the read loop...
                # WE WILL DEADLOCK.
                asyncio.create_task(self.fetch_and_broadcast(uri))
             except Exception as e:
                logger.error(f"Error handling notification: {e}")

    async def fetch_and_broadcast(self, uri):
        try:
             res = await self.read_resource(uri)
             if res.contents:
                content = res.contents[0].text
                await a2ui_queue.put({"type": "a2ui_update", "uri": uri, "content": content})
        except Exception as e:
             logger.error(f"Failed to fetch updated resource {uri}: {e}")

class MCPClientManager:
    def __init__(self):
        self.exit_stack = None
        self.session = None

    async def start(self):
        # Start the backend.py subprocess
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "backend"],
            env=os.environ.copy()
        )

        from contextlib import AsyncExitStack
        self.exit_stack = AsyncExitStack()

        read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self.exit_stack.enter_async_context(ADKClientSession(read_stream, write_stream))

        await self.session.initialize()
        logger.info("MCP Client Initialized and Connected to Backend")

    async def stop(self):
        if self.exit_stack:
            await self.exit_stack.aclose()


mcp_manager = MCPClientManager()

# --- HTTP Endpoints ---

async def rpc_endpoint(request):
    """Handle JSON-RPC requests."""
    body = await request.body()
    response = JSONRPCResponseManager.handle(body.decode("utf-8"), dispatcher)
    return Response(response.json, media_type="application/json")

@dispatcher.add_method
def sendMessage(message: str, session_id: str = "default"):
    """JSON-RPC method to send a message to the agent."""
    # We need to run the agent in the background or await it?
    # JSON-RPC is typically sync-ish in response structure, but we want to trigger streaming.
    # We will return "Accepted" and stream results via SSE.
    asyncio.create_task(run_agent_turn(message, session_id))
    return "Message received, processing..."

async def run_agent_turn(message: str, session_id: str):
    logger.info(f"Processing message: {message} for session {session_id}")

    # Send "typing" or similar is not supported by ADK explicit event yet likely, but we can push to queue.

    current_message = types.Content(
        role="user", parts=[types.Part.from_text(text=message)]
    )

    try:
        # Assuming FlightAgentAsync defined in agent.py
        # We need to use the runner.
        # CAUTION: flight_agent.agent is the adk object.
        # We need a Runner instance.

        # Ensure session exists
        session = await runner.session_service.get_session(
            app_name=flight_agent.agent.name,
            user_id="user",
            session_id=session_id
        )
        if not session:
             session = await runner.session_service.create_session(
                app_name=flight_agent.agent.name,
                user_id="user",
                session_id=session_id
            )

        async for event in runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=current_message
        ):
            # Check for final response
            if event.is_final_response():
                if event.content and event.content.parts:
                    text_parts = []
                    for p in event.content.parts:
                        if p.text:
                            text_parts.append(p.text)

                    full_text = "\n".join(text_parts)

                    # Split A2UI if present
                    if "---a2ui_JSON---" in full_text:
                        text, json_str = full_text.split("---a2ui_JSON---", 1)
                        # Push text to Chat
                        if text.strip():
                            await chat_queue.put({"type": "chat_message", "content": text.strip()})
                        # Push JSON to A2UI
                        if json_str.strip():
                             await a2ui_queue.put({"type": "a2ui_render", "content": json_str.strip()})
                    else:
                        await chat_queue.put({"type": "chat_message", "content": full_text})

            # Use intermediate events if needed (like "thinking...")

    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)
        await chat_queue.put({"type": "error", "content": str(e)})


async def chat_events(request):
    """SSE endpoint for chat messages."""
    async def event_generator():
        while True:
            item = await chat_queue.get()
            yield {"data": json.dumps(item)}
            chat_queue.task_done()
    return EventSourceResponse(event_generator())

async def a2ui_events(request):
    """SSE endpoint for A2UI updates."""
    async def event_generator():
        while True:
            item = await a2ui_queue.get()
            yield {"data": json.dumps(item)}
            a2ui_queue.task_done()
    return EventSourceResponse(event_generator())

# --- Lifecycle ---

async def startup():
    global flight_agent, runner
    await mcp_manager.start()
    flight_agent = FlightAgent(mcp_session=mcp_manager.session)
    runner = Runner(
        app_name=flight_agent.agent.name,
        agent=flight_agent.agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

async def shutdown():
    await mcp_manager.stop()

routes = [
    Route("/rpc", rpc_endpoint, methods=["POST"]),
    Route("/events/chat", chat_events),
    Route("/events/a2ui", a2ui_events),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    await startup()
    yield
    await shutdown()

app = Starlette(
    routes=routes,
    middleware=middleware,
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
