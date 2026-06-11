"""Central coordinator daemon and leaderboard lock manager for A2UI Express.

Reads leaderboard.json, launches Antigravity worker subagents via agentapi,
reactively validates completion payloads, and enforces atomic write locking.
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
from typing import Any, Optional

SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEADERBOARD_PATH = os.path.join(SPEC_EXPRESS_DIR, "leaderboard.json")


class EvolutionCoordinator:
    """Manages blackboard file locks and dispatches Antigravity workers."""

    def __init__(self, leaderboard_path: str = LEADERBOARD_PATH):
        """Initializes coordinator with disk path to central leaderboard."""
        self.leaderboard_path = leaderboard_path

    def read_leaderboard_locked(self) -> dict[str, Any]:
        """Acquires a shared lock and reads the central leaderboard registry."""
        if not os.path.exists(self.leaderboard_path):
            return {"reigning_champion": "gene_v1_0", "history": {}}

        with open(self.leaderboard_path, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
        return data

    def record_champion_locked(self, candidate_payload: dict[str, Any]) -> bool:
        """Acquires an exclusive write lock and updates champion if score beats baseline.

        Args:
            candidate_payload: JSON dict yielded by worker_entrypoint completion.

        Returns:
            True if candidate achieved a new high score and was recorded, False otherwise.
        """
        candidate_id = candidate_payload.get("candidate_id")
        new_score = candidate_payload.get("fitness_score", 0.0)

        if not candidate_id or candidate_payload.get("status") != "success":
            print(f"Rejecting malformed or failed payload: {candidate_id}")
            return False

        with open(self.leaderboard_path, "r+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            board = json.load(f)

            reigning_id = board.get("reigning_champion", "gene_v1_0")
            reigning_meta = board.get("history", {}).get(reigning_id, {})
            reigning_score = reigning_meta.get("fitness_score", 0.0)

            print(f"Evaluating candidate {candidate_id} ({new_score}) vs Champion {reigning_id} ({reigning_score})")

            if new_score > reigning_score:
                print(f"*** NEW CHAMPION DISCOVERED: {candidate_id} ***")
                board["reigning_champion"] = candidate_id
                if "history" not in board:
                    board["history"] = {}
                board["history"][candidate_id] = {
                    "parent": candidate_payload.get("parent_id"),
                    "fitness_score": new_score,
                    "metrics": candidate_payload.get("metrics", {}),
                    "artifacts_dir": candidate_payload.get("artifacts_dir"),
                }

                f.seek(0)
                f.truncate()
                json.dump(board, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
                return True

            fcntl.flock(f, fcntl.LOCK_UN)
            print("Candidate score did not beat reigning champion. Discarding.")
            return False

    def dispatch_worker_subagents(self, num_workers: int = 5) -> None:
        """Dispatches parallel worker subagent conversations using agentapi CLI."""
        board = self.read_leaderboard_locked()
        champion_id = board.get("reigning_champion", "gene_v1_0")

        print(f"Dispatching {num_workers} Antigravity worker conversations mutating {champion_id}...")

        for i in range(1, num_workers + 1):
            prompt = (
                f"Invoke the ExpressMutatorWorker subagent with Workspace mode 'inherit'. "
                f"Instruct it to run precisely: {sys.executable} -m specification.v1_0.express.optimizer.worker_entrypoint "
                f"--parent_id {champion_id} --model_name gemini-3-pro-preview --thinking_budget 16384. Report completion payload back to coordinator via send_message."
            )
            cmd = ["agentapi", "new-conversation", "--model=pro", prompt]
            print(f"Launching worker {i}/{num_workers}: {' '.join(cmd)}")
            try:
                # Launch asynchronously in background
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("Error: agentapi CLI executable not found on PATH. Skipping background dispatch.")
                break


def main():
    """Parses CLI commands for coordinator daemon."""
    parser = argparse.ArgumentParser(description="A2UI Express Central Coordinator Daemon")
    parser.add_argument("--dispatch", type=int, metavar="N", help="Dispatch N parallel workers")
    parser.add_argument("--record_payload", type=str, help="Disk path to worker JSON payload file to record")
    args = parser.parse_args()

    coord = EvolutionCoordinator()

    if args.dispatch:
        coord.dispatch_worker_subagents(args.dispatch)
    elif args.record_payload:
        if not os.path.exists(args.record_payload):
            print(f"Payload file not found: {args.record_payload}")
            sys.exit(1)
        with open(args.record_payload, "r", encoding="utf-8") as f:
            payload = json.load(f)
        coord.record_champion_locked(payload)
    else:
        board = coord.read_leaderboard_locked()
        print(json.dumps(board, indent=2))


if __name__ == "__main__":
    main()
