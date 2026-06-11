"""Central coordinator daemon and leaderboard lock manager for A2UI Express.

Reads leaderboard.json, initializes temporary git repository sandboxes,
allocates isolated git worktrees per subagent, and reactively enforces locks.
"""

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Optional

SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEADERBOARD_PATH = os.path.join(SPEC_EXPRESS_DIR, "leaderboard.json")


class EvolutionCoordinator:
    """Manages blackboard file locks and bootstraps disposable worktree sandboxes."""

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

        if not candidate_id or new_score == 0.0:
            return False

        with open(self.leaderboard_path, "r+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            board = json.load(f)

            reigning_id = board.get("reigning_champion", "gene_v1_0")
            reigning_score = board.get("history", {}).get(reigning_id, {}).get("fitness_score", 0.85)

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

    def bootstrap_temporary_git_repository(self) -> str:
        """Bootstraps a disposable root git repository for isolated subagent branching."""
        scratch_dir = os.path.abspath(os.path.join(SPEC_EXPRESS_DIR, "..", "..", "..", "scratch"))
        repo_dir = os.path.join(scratch_dir, "mutation_repo")
        worktrees_dir = os.path.join(scratch_dir, "worktrees")

        os.makedirs(repo_dir, exist_ok=True)
        os.makedirs(worktrees_dir, exist_ok=True)

        # If git repository is already active and committed, return immediately
        if os.path.exists(os.path.join(repo_dir, ".git")):
            return repo_dir

        print(f"Bootstrapping pristine temporary root git repository at: {repo_dir}")
        subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True)

        # Populate core artifacts required for independent baseline loading and compilation
        core_files = [
            "compiler.py", "decompiler.py", "test_express.py",
            "a2ui_express.md", "basic_prompt.md"
        ]
        for fname in core_files:
            src = os.path.join(SPEC_EXPRESS_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(repo_dir, fname))

        # Copy optimizer infrastructure package
        opt_src = os.path.join(SPEC_EXPRESS_DIR, "optimizer")
        opt_dst = os.path.join(repo_dir, "optimizer")
        if os.path.exists(opt_src) and not os.path.exists(opt_dst):
            shutil.copytree(opt_src, opt_dst, dirs_exist_ok=True)

        # Commit baseline state
        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Bootstrap disposable AST mutation baseline"], cwd=repo_dir, check=True, capture_output=True)

        return repo_dir

    def dispatch_worker_subagents(self, num_workers: int = 5) -> None:
        """Dispatches parallel agentic subagents assigned to isolated git worktrees."""
        board = self.read_leaderboard_locked()
        champion_id = board.get("reigning_champion", "gene_v1_0")

        # Bootstrap temporary root git repository
        repo_dir = self.bootstrap_temporary_git_repository()
        worktrees_dir = os.path.abspath(os.path.join(repo_dir, "..", "worktrees"))

        print(f"Dispatching {num_workers} write-enabled agentic worktree sessions mutating {champion_id}...")

        for i in range(1, num_workers + 1):
            wt_path = os.path.join(worktrees_dir, f"worker_{i}")
            prompt = (
                f"Navigate to temporary git repository: {repo_dir}. "
                f"Create an isolated git worktree branch: git worktree add {wt_path} -b mutate_branch_{i}. "
                f"Change directory into your assigned worktree ({wt_path}). Use view_file to inspect compiler.py and test_express.py. "
                f"Apply surgical AST diff edits using replace_file_content to mutate character matching strings as instructed in optimizer/mutate_prompt.md. "
                f"Execute unit tests interactively: python3 -m unittest test_express.py inside your worktree sandbox until passing 100%. "
                f"Once verified green, compute fitness metrics and report your winning candidate payload back to coordinator via send_message."
            )
            cmd = ["agentapi", "new-conversation", "--model=pro", prompt]
            print(f"Launching agentic worktree session {i}/{num_workers}: {wt_path}")
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("Error: agentapi CLI executable not found on host PATH. Skipping terminal dispatch.")
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
