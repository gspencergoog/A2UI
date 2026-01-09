# Flight Booking MCP Demo

This demo showcases an ADK Agent that wraps an MCP Server to provide a rich UI flight booking experience using A2UI.

## Architecture

- **`backend.py`**: An MCP Server (using standard MCP Python SDK) that provides `search_flights` and `book_flight` tools. It maintains the state of UI resources.
- **`agent.py`**: An ADK Agent that connects to the MCP Server via stdio. It exposes the MCP tools to the LLM and intercepts the results to fetch A2UI content.
- **`adk_server.py`**: A Starlette HTTP server that exposes:
    - `POST /rpc`: JSON-RPC endpoint for sending messages to the agent.
    - `GET /events/chat`: SSE stream for text/chat responses.
    - `GET /events/a2ui`: SSE stream for A2UI JSONL updates.

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```
   (Or use `uv sync`)

2. Set your Google Cloud Project / API Key for ADK:
   ```bash
   export GOOGLE_GENAI_API_KEY=...
   # or
   export VERTEX_API_KEY=...
   ```

## Running

Run the server:

```bash
# Run from the flight_booking directory
python .
# OR
python __main__.py
```

## Usage

Use a client that supports JSON-RPC and SSE to interact with `http://localhost:8000`.

**Send Message (JSON-RPC):**
```json
{
  "jsonrpc": "2.0",
  "method": "sendMessage",
  "params": {"message": "I want to fly to Paris", "session_id": "test1"},
  "id": 1
}
```

**Listen for Chat:**
`GET /events/chat`

**Listen for UI:**
`GET /events/a2ui`
