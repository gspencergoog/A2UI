import logging
import json
from typing import Any, Dict, List, Optional
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext
import mcp.types as types
from mcp.client.session import ClientSession

logger = logging.getLogger(__name__)

class FlightAgent:
    def __init__(self, mcp_session: ClientSession, model_name: str = "gemini/gemini-2.0-flash-exp"):
        self.mcp_session = mcp_session
        self.agent = LlmAgent(
            model=LiteLlm(model=model_name),
# RE-WRITING CLASS with async tools for now.

class FlightAgent:
    def __init__(self, mcp_session: ClientSession, model_name: str = "gemini/gemini-2.0-flash-exp"):
        self.mcp_session = mcp_session
        self.agent = LlmAgent(
            model=LiteLlm(model=model_name),
            name="flight_agent",
            description="A helpful flight booking agent that can search and book flights.",
            instruction="You are a flight booking assistant. Use the available tools to search for flights and book them. When you search for flights, you will receive a UI to show to the user. Always present this UI. When booking, use the information provided in the UI context.",
            tools=[self.search_flights, self.book_flight]
        )

    async def search_flights(self, destination: str, tool_context: ToolContext) -> str:
        """Search for flights to a destination. Returns a summary and a UI."""
        logger.info(f"Searching flights to {destination}")
        result = await self.mcp_session.call_tool(
            "search_flights",
            arguments={"destination": destination}
        )

        # The MCP tool returns a TextContent and a meta with uri.
        # We want to fetch the UI resource.
        content_text = ""
        uri = None

        if result.content:
            for c in result.content:
                if c.type == "text":
                    content_text += c.text

        if result._meta and "ui_resource_uri" in result._meta:
            uri = result._meta["ui_resource_uri"]
            # Fetch the UI
            try:
                # read_resource returns a ReadResourceResult, we need the valid content.
                # Assuming generic client structure.
                # Wait, mcp.client.session.ClientSession.read_resource returns valid result object.
                resource_res = await self.mcp_session.read_resource(uri)
                # resource_res.contents is a list of ResourceContent (TextResourceContent or BlobResourceContent)
                # We expect JSON in text.
                if resource_res.contents:
                     ui_json_str = resource_res.contents[0].text
                     # Append the UI JSON to the output for the ADK/Client to see.
                     # We use the ---a2ui_JSON--- delimiter as seen in contact_lookup
                     return f"{content_text}\n\n---a2ui_JSON---\n{ui_json_str}\n"
            except Exception as e:
                logger.error(f"Failed to fetch resource {uri}: {e}")
                return f"{content_text}\n(Failed to load UI: {e})"

        return content_text

    async def book_flight(self, flight_id: str, resource_uri: str, tool_context: ToolContext) -> str:
        """Book a flight given its ID and the UI resource URI."""
        logger.info(f"Booking flight {flight_id} on {resource_uri}")
        result = await self.mcp_session.call_tool(
            "book_flight",
            arguments={"flight_id": flight_id, "resource_uri": resource_uri}
        )
        # Booking might update the resource, which will trigger a notification.
        # We just return the text confirmation here.
        content_text = ""
        if result.content:
             for c in result.content:
                if c.type == "text":
                    content_text += c.text

        return content_text
