import asyncio
import json
import uuid
from typing import Dict, Any, List
from mcp.server.models import InitializationOptions
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
import mcp.types as types

# Initialize the MCP Server
server = Server("gemini-a2ui-resource-demo")

# In-memory storage for UI resources (keyed by URI)
# Each entry is a list of A2UI messages (the "stream")
ui_store: Dict[str, List[Dict[str, Any]]] = {}

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List currently active UI resources."""
    return [
        types.Resource(
            uri=uri,
            name=f"A2UI Surface {uri.split('/')[-1]}",
            mimeType="application/json",
            description="Addressable A2UI state for a specific interactive surface."
        )
        for uri in ui_store.keys()
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Return the A2UI JSONL stream for a given resource URI."""
    if uri in ui_store:
        # The protocol technically uses JSONL, but we return a JSON array
        # for the MCP resource payload which the client can iterate over.
        return json.dumps(ui_store[uri])
    raise ValueError(f"Resource not found: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List tools that return UI Resource pointers."""
    return [
        types.Tool(
            name="search_flights",
            description="Search for flights. Returns a text summary and a URI for the rich UI.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "e.g. SJC, JFK, London"}
                },
                "required": ["destination"]
            }
        ),
        types.Tool(
            name="book_flight",
            description="Book a specific flight. Updates the associated UI resource.",
            inputSchema={
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string"},
                    "resource_uri": {"type": "string", "description": "The URI of the UI to update"}
                },
                "required": ["flight_id", "resource_uri"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> types.CallToolResult:
    """Handle tool calls and manage Resource lifecycle."""

    if name == "search_flights":
        dest = arguments.get("destination", "Destination")
        # Generate a unique URI for this specific search result
        session_id = str(uuid.uuid4())[:8]
        resource_uri = f"mcp://demo/ui/flights_{session_id}"

        # Construct A2UI Protocol Messages (compliant with standard catalog)
        a2ui_payload = [
            {
                "surfaceUpdate": {
                    "surfaceId": "flight_surface",
                    "components": [
                        {
                            "id": "root",
                            "component": { "Card": { "child": "flight_row" } }
                        },
                        {
                            "id": "flight_row",
                            "component": {
                                "Row": {
                                    "distribution": "spaceBetween",
                                    "alignment": "center",
                                    "children": {"explicitList": ["text_content", "book_btn"]}
                                }
                            }
                        },
                        {
                            "id": "text_content",
                            "component": {
                                "Text": { "text": { "literalString": f"Flight to {dest}: $148 (Direct)" } }
                            }
                        },
                        {
                            "id": "book_btn",
                            "component": {
                                "Button": {
                                    "child": "btn_label",
                                    "primary": True,
                                    "action": {
                                        "name": "book_flight",
                                        "context": [
                                            {"key": "flight_id", "value": {"literalString": f"UA-{session_id}"}},
                                            {"key": "resource_uri", "value": {"literalString": resource_uri}}
                                        ]
                                    }
                                }
                            }
                        },
                        { "id": "btn_label", "component": { "Text": { "text": { "literalString": "Book Now" } } } }
                    ]
                }
            },
            {
                "beginRendering": {
                    "surfaceId": "flight_surface",
                    "root": "root"
                }
            }
        ]

        # Save to store
        ui_store[resource_uri] = a2ui_payload

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"I found a flight to {dest} for $148. You can confirm it in the UI."
                )
            ],
            _meta={
                "ui_resource_uri": resource_uri
            }
        )

    if name == "book_flight":
        fid = arguments.get("flight_id")
        uri = arguments.get("resource_uri")

        if uri not in ui_store:
            raise ValueError("Interactive session expired or URI invalid.")

        # 1. Update the Resource state (Mutate the UI to show success)
        success_payload = [
            {
                "surfaceUpdate": {
                    "surfaceId": "flight_surface",
                    "components": [
                        {
                            "id": "success_root",
                            "component": {
                                "Column": {
                                    "alignment": "center",
                                    "children": {"explicitList": ["icon", "msg"]}
                                }
                            }
                        },
                        { "id": "icon", "component": { "Icon": { "name": { "literalString": "check" } } } },
                        { "id": "msg", "component": { "Text": { "text": { "literalString": f"Booked {fid}!" }, "usageHint": "h2" } } }
                    ]
                }
            },
            {
                "beginRendering": { "surfaceId": "flight_surface", "root": "success_root" }
            }
        ]
        ui_store[uri] = success_payload

        # 2. THE PUSH: Notify the client that the resource has changed
        # The client should see this and immediately trigger a resource/read
        await server.request_context.session.send_notification(
            types.ResourceUpdatedNotification(
                method="notifications/resources/updated",
                params=types.ResourceUpdatedNotificationParams(uri=uri)
            )
        )

        # 3. Inform the LLM via synthetic turn injection
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"The user has successfully booked flight {fid}. Confirmation: CONF-A2UI."
                )
            ]
        )

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-a2ui-resource-demo",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())