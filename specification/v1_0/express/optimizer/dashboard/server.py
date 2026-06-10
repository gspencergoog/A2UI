"""Real-time monitoring HTTP server and REST API backend for A2UI Express dashboard.

Serves single-page HTML assets and exposes JSON REST endpoints inspecting
leaderboard.json, scanning active Jetski transcripts in brain, and checking MLX.
"""

import argparse
import fcntl
import http.server
import json
import os
import socket
import socketserver
import sys
from typing import Any, Optional

DASHBOARD_DIR = os.path.abspath(os.path.dirname(__file__))
SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(DASHBOARD_DIR, "..", ".."))
LEADERBOARD_PATH = os.path.join(SPEC_EXPRESS_DIR, "leaderboard.json")
JETSKI_BRAIN_DIR = os.path.expanduser("~/.gemini/jetski/brain")


class DashboardAPIHandler(http.server.SimpleHTTPRequestHandler):
    """Handles static asset serving and asynchronous REST API queries."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def _send_json_response(self, data: dict[str, Any], status_code: int = 200) -> None:
        """Serializes dictionary payload and sends HTTP JSON headers."""
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _get_leaderboard_data(self) -> dict[str, Any]:
        """Reads locked central leaderboard registry."""
        if not os.path.exists(LEADERBOARD_PATH):
            return {"reigning_champion": "gene_v1_0", "history": {}}

        try:
            with open(LEADERBOARD_PATH, "r", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
            return data
        except (IOError, ValueError, json.JSONDecodeError):
            return {"reigning_champion": "gene_v1_0", "history": {}, "error": "Registry locked or malformed"}

    def _get_active_agents_data(self) -> dict[str, Any]:
        """Inspects recent Jetski conversation transcripts in brain directory."""
        agents = []
        recent_logs = []

        if not os.path.exists(JETSKI_BRAIN_DIR):
            return {"agents": agents, "recent_logs": recent_logs, "error": "Brain directory not found"}

        try:
            # Sort conversation folders by modification time (most recent first)
            subdirs = [
                os.path.join(JETSKI_BRAIN_DIR, d)
                for d in os.listdir(JETSKI_BRAIN_DIR)
                if os.path.isdir(os.path.join(JETSKI_BRAIN_DIR, d))
            ]
            subdirs.sort(key=os.path.getmtime, reverse=True)

            # Inspect top 10 most recent conversations for worker activity
            for conv_dir in subdirs[:10]:
                log_path = os.path.join(conv_dir, ".system_generated", "logs", "transcript.jsonl")
                if not os.path.exists(log_path):
                    continue

                conv_id = os.path.basename(conv_dir)
                last_thinking = ""
                last_status = "RUNNING"
                current_gate = "Tier 0/1 Unit Tests"

                # Read last 50 lines of transcript
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()[-50:]

                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        if "thinking" in entry and entry["thinking"]:
                            last_thinking = entry["thinking"]
                        if "status" in entry:
                            last_status = entry["status"]
                        if "gate" in entry or "Tier" in entry.get("content", ""):
                            current_gate = entry.get("gate", "Tier 2 MLX Linting")

                        # Collect recent model logs for terminal tailing view
                        if entry.get("source") == "MODEL" and len(recent_logs) < 30:
                            recent_logs.append({
                                "created_at": entry.get("created_at", "").replace("2026-06-10T", "").replace("Z", ""),
                                "source": entry.get("type", "MODEL"),
                                "status": entry.get("status", "DONE"),
                                "content": entry.get("content", entry.get("thinking", "")),
                            })
                    except (json.JSONDecodeError, KeyError):
                        continue

                if last_thinking or "ExpressMutatorWorker" in "".join(lines):
                    agents.append({
                        "conversation_id": conv_id[:12],
                        "status": last_status,
                        "current_gate": current_gate,
                        "thinking": last_thinking[:400] + ("..." if len(last_thinking) > 400 else ""),
                    })

        except (IOError, OSError) as e:
            print(f"Error reading brain transcripts: {e}")

        return {"agents": agents, "recent_logs": recent_logs[:30]}

    def _get_system_state(self) -> dict[str, Any]:
        """Checks socket connection on localhost port 8080 to verify MLX server status."""
        mlx_online = False
        try:
            with socket.create_connection(("localhost", 8080), timeout=0.5):
                mlx_online = True
        except (OSError, socket.timeout, ConnectionRefusedError):
            mlx_online = False

        return {"mlx_online": mlx_online}

    def do_GET(self) -> None:
        """Routes HTTP GET requests to REST APIs or static asset handler."""
        if self.path == "/api/leaderboard":
            self._send_json_response(self._get_leaderboard_data())
        elif self.path == "/api/agents":
            self._send_json_response(self._get_active_agents_data())
        elif self.path == "/api/system_state":
            self._send_json_response(self._get_system_state())
        else:
            # Fall back to native static file serving from DASHBOARD_DIR
            super().do_GET()


def main():
    """Parses arguments and launches standalone dashboard HTTP server."""
    parser = argparse.ArgumentParser(description="A2UI Express Optimizer Dashboard Server")
    parser.add_argument("--port", type=int, default=8081, help="HTTP listening port")
    args = parser.parse_args()

    # Ensure socket address reuse
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", args.port), DashboardAPIHandler) as httpd:
            print(f"=== A2UI Express Dashboard Backend active on http://localhost:{args.port} ===")
            print(f"Serving UI static assets from: {DASHBOARD_DIR}")
            print(f"Monitoring central registry at: {LEADERBOARD_PATH}")
            print(f"Scanning active agent logs in: {JETSKI_BRAIN_DIR}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server.")
        sys.exit(0)
    except OSError as e:
        print(f"Error binding server to port {args.port}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
