import pytest
import asyncio
import json
import logging
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from starlette.testclient import TestClient
from mcp.client.session import ClientSession
from mcp import StdioServerParameters, ClientSession
import mcp.types as types
from google.genai import types as genai_types

# Add samples to path so we can import modules
# sys.path.append(os.getcwd())

# We need to mock the real MCP connection IF we don't want to spawn subprocesses in unit tests,
# BUT the user asked to "try it out via the test", implying an integration test might be desired.
# However, spawning real subprocesses in a test suite can be flaky if dependencies aren't perfect.
# Given "create that test so we can try it out", I will try to make it as real as possible,
# but maybe mock the `google-adk`'s LLM calls because we don't want to burn keys/credits or rely on network.
# We DEFINITELY should mock the LLM.
# We SHOULD use the real MCP server if possible to test that integration,
# OR mock the MCP session if we only care about the ADK server logic.
# Let's try to mock the LLM but keep the MCP server real?
# Using `python samples/mcp/flight_booking/backend.py` requires `mcp` installed.
# Using `google-adk` requires auth.
# So I MUST mock the LLM response.

# I will update `agent.py` or use `patch` to mock `LlmAgent` execution or the `LiteLlm` model?
# `google-adk`'s `Runner.run_async` calls the agent.
# If I mock the `model` in `FlightAgent`, I can control the output.

from adk_server import app, startup, shutdown, mcp_manager
import agent

@pytest.fixture
def mock_llm_response():
    """Mock the LLM to return specific tool calls or text."""
    # We can patch `LiteLlm.generate_response` or similar?
    # Actually `google-adk` uses `model.generate_content`.
    pass

# We will write a test using `TestClient` but `TestClient` is sync.
# `adk_server` uses `asyncio` for queues.
# We need `AsyncClient`.

from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_flight_search_flow():
    # 1. Setup - Mock the LLM to call the 'search_flights' tool
    # We need to patch the `LlmAgent` or the `Runner`?
    # Actually, let's verify if we can just mock the MCP session for stability first?
    # No, let's try to trust the user wants to test the ADK logic mainly.

    # It's hard to mock `google-adk` internals easily without deeper knowledge.
    # But we can assume the agent will call the tool if we give it a clear prompt?
    # No, without an API key `google-adk` will fail on initialization or run.
    # SO WE MUST MOCK `google-adk` model.

    # We will mock `FlightAgent` in `adk_server`?
    # Or just patch `LiteLlm` in `agent.py`.

    with patch("agent.Gemini") as MockGemini:
        # Mock instance
        mock_model = MockGemini.return_value

        # When `agent.run` happens...
        # Wait, `google-adk` is complex.
        # Let's just mock `FlightAgent` methods?
        # No, `adk_server` uses `runner.run_async`.

        # Let's use `TestClient` but acknowledge we might need to manually trigger things if we can't run full ADK.
        pass

    # Actually, creating a "good coverage" test that "tries it out" usually implies running the code.
    # If I can't run ADK without a key, I can't really "try it out" fully.
    # I will assume the user HAS these keys or I should mock the MCP/ADK interaction points.

    # Let's write a test that mocks the `FlightAgent` to return a predefined event stream.
    # This verifies the Server logic (RPC -> Queue -> SSE).

    # Step 1: Start logic
    # We need to manually call `startup` to init globals if we use `app` directly?
    # `TestClient` calls startup handlers.

    # Mock MCP Client start/stop to avoid spawning processes
    with patch("adk_server.mcp_manager.start", new_callable=AsyncMock) as mock_mcp_start, \
         patch("adk_server.mcp_manager.stop", new_callable=AsyncMock) as mock_mcp_stop:

        # We also need to mock `FlightAgent` to avoid real ADK init (LiteLlm needs key?)
        # Let's assume we patch `adk_server.FlightAgent` class.
        with patch("adk_server.FlightAgent") as MockFlightAgent, \
             patch("adk_server.Runner") as MockRunner:

            # Setup mocks
            mock_agent_instance = MockFlightAgent.return_value
            mock_agent_instance.agent.name = "flight_agent"

            mock_runner_instance = MockRunner.return_value
            mock_runner_instance.session_service.get_session = AsyncMock(return_value=MagicMock(id="sess1"))
            mock_runner_instance.session_service.create_session = AsyncMock(return_value=MagicMock(id="sess1"))

            # Mock run_async to yield a response
            async def mock_run_async(*args, **kwargs):
                # Yield a fake response
                # We need to match `google.genai.types` structure somewhat or just generic object
                # Event.is_final_response() -> True
                # Event.content.parts -> [Part(text="Found flights..."), Part(text="---a2ui_JSON---...")]

                yield MagicMock(
                    is_final_response=lambda: True,
                    content=MagicMock(
                        parts=[
                            MagicMock(text="I found some flights to Paris."),
                            MagicMock(text="\n\n---a2ui_JSON---\n" + json.dumps([{"surfaceUpdate": {"surfaceId": "test"}}]))
                        ]
                    )
                )

            mock_runner_instance.run_async = mock_run_async

            # Manually run startup to init globals
            await startup()

            try:
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                    # 1. Start SSE connections
                    # We can't easily wait for SSE in `httpx` without streaming.
                    # We'll trigger the RPC first, then verify queues?
                    # Or connect SSE first.

                    # Using `acyncio.gather` to run SSE listener and RPC trigger?

                    # Let's just trigger RPC and check the global queues in `adk_server`.
                    # This is a white-box test.

                    rpc_payload = {
                        "jsonrpc": "2.0",
                        "method": "sendMessage",
                        "params": {"message": "Fly to Paris", "session_id": "test1"},
                        "id": 1
                    }

                    response = await client.post("/rpc", json=rpc_payload)
                    assert response.status_code == 200
                    assert response.json()["result"] == "Message received, processing..."

                    # Allow async task to run
                    await asyncio.sleep(0.1)

                    # Check Chat Queue
                    from adk_server import chat_queue, a2ui_queue

                    assert not chat_queue.empty()
                    chat_msg = await chat_queue.get()
                    assert chat_msg["type"] == "chat_message"
                    assert "I found some flights" in chat_msg["content"]

                    # Check A2UI Queue
                    assert not a2ui_queue.empty()
                    a2ui_msg = await a2ui_queue.get()
                    assert a2ui_msg["type"] == "a2ui_render"
                    assert "surfaceUpdate" in a2ui_msg["content"]
            finally:
                await shutdown()

@pytest.mark.asyncio
async def test_mcp_notification_flow():
    # Test that notifications from MCP push to A2UI queue

    # Mock the session in mcp_manager
    from adk_server import mcp_manager, a2ui_queue

@pytest.mark.asyncio
async def test_mcp_notification_flow():
    # Test that notifications from MCP push to A2UI queue
    from adk_server import ADKClientSession, a2ui_queue
    import mcp.types as types

    # Mock the session streams
    mock_read = AsyncMock()
    mock_write = AsyncMock()

    session = ADKClientSession(mock_read, mock_write)

    # Mock read_resource to return content
    session.read_resource = AsyncMock(return_value=MagicMock(contents=[MagicMock(text="{\"new\": \"ui\"}")]))

    # Create a fake notification
    notification = types.ResourceUpdatedNotification(
        method="notifications/resources/updated",
        params=types.ResourceUpdatedNotificationParams(uri="mcp://test")
    )

    # Call the handler directly
    await session._received_notification(notification)

    # Allow async tasks to complete (fetch_and_broadcast)
    await asyncio.sleep(0.1)

    # Check queue
    assert not a2ui_queue.empty()
    msg = await a2ui_queue.get()
    assert msg["type"] == "a2ui_update"
    assert str(msg["uri"]) == "mcp://test"
    assert "new" in msg["content"]

