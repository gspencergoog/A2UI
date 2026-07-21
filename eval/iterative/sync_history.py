#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Synchronizes archived history runs across multiple parallel worktrees into a single master history."""

import argparse
import glob
import os
import shutil
import sys
from typing import List, Optional

# Add parent directory to sys.path to import optimize_format
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from optimize_format import (  # type: ignore[import-not-found]
    regenerate_master_index,
)


def _get_max_run_id(history_dir: str) -> int:
    """Finds the maximum integer run ID existing in history_dir."""
    max_id = 0
    if os.path.exists(history_dir):
        for entry in os.scandir(history_dir):
            if entry.is_dir() and entry.name.startswith("run_"):
                parts = entry.name.split("_")
                if len(parts) >= 2 and parts[1].isdigit():
                    max_id = max(max_id, int(parts[1]))
    return max_id


def sync_worktree_history(
    target_worktrees: Optional[List[str]] = None,
    skip_index_regen: bool = False,
) -> List[str]:
    """Scans target worktrees and syncs missing history run folders into main history with zero collisions."""
    main_history_dir = os.path.join(SCRIPT_DIR, "history")
    os.makedirs(main_history_dir, exist_ok=True)

    if not target_worktrees:
        # Default: search for sibling worktrees under ../worktrees/ or ../
        parent_dir = os.path.normpath(os.path.join(SCRIPT_DIR, "../../.."))
        worktrees_dir = os.path.join(parent_dir, "worktrees")
        target_worktrees = []
        if os.path.exists(worktrees_dir):
            for entry in os.scandir(worktrees_dir):
                if entry.is_dir():
                    target_worktrees.append(entry.path)

        # Also search direct sibling directories under parent_dir
        if os.path.exists(parent_dir):
            for entry in os.scandir(parent_dir):
                if entry.is_dir() and entry.name != "worktrees":
                    target_worktrees.append(entry.path)

    copied_runs = []
    current_max_id = _get_max_run_id(main_history_dir)

    # Pre-cache existing history folder names and occupied run IDs
    existing_dirs = {e.name for e in os.scandir(main_history_dir) if e.is_dir()}
    occupied_ids = set()
    for d_name in existing_dirs:
        if d_name.startswith("run_"):
            d_parts = d_name.split("_")
            if len(d_parts) >= 2 and d_parts[1].isdigit():
                occupied_ids.add(int(d_parts[1]))

    for wt in target_worktrees:
        wt_history = os.path.join(wt, "eval", "iterative", "history")
        if not os.path.exists(wt_history):
            continue

        for entry in sorted(os.scandir(wt_history), key=lambda e: e.name):
            if entry.is_dir() and entry.name.startswith("run_"):
                # Exact folder match check (already synced)
                exact_dest = os.path.join(main_history_dir, entry.name)
                if entry.name in existing_dirs:
                    continue

                parts = entry.name.split("_")
                run_id_num = (
                    int(parts[1]) if (len(parts) >= 2 and parts[1].isdigit()) else None
                )

                id_occupied = (
                    run_id_num in occupied_ids if run_id_num is not None else False
                )

                if id_occupied:
                    # Re-index incoming folder with next available max_id
                    current_max_id += 1
                    new_id_str = f"{current_max_id:03d}"
                    parts[1] = new_id_str
                    new_name = "_".join(parts)
                    dest_dir = os.path.join(main_history_dir, new_name)
                else:
                    dest_dir = exact_dest
                    if run_id_num is not None and run_id_num > current_max_id:
                        current_max_id = run_id_num

                try:
                    shutil.copytree(entry.path, dest_dir)
                    bname = os.path.basename(dest_dir)
                    copied_runs.append(bname)
                    existing_dirs.add(bname)
                    assigned_id = current_max_id if id_occupied else run_id_num
                    if assigned_id is not None:
                        occupied_ids.add(assigned_id)
                except FileExistsError:
                    pass
                except Exception:
                    if os.path.exists(dest_dir):
                        shutil.rmtree(dest_dir)
                    raise

    # Rebuild master index if requested
    if not skip_index_regen:
        from optimize_format import regenerate_master_index  # type: ignore[import-not-found]

        regenerate_master_index(SCRIPT_DIR)
    return copied_runs


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Sync history run directories from parallel worktrees into main history."
        )
    )
    parser.add_argument(
        "--worktree",
        "-w",
        action="append",
        dest="worktrees",
        help=(
            "Path to worktree directory to sync history from (can be specified multiple"
            " times)"
        ),
    )

    args = parser.parse_args(argv)
    synced = sync_worktree_history(args.worktrees)

    if synced:
        print(
            f"Successfully synchronized {len(synced)} history runs: {', '.join(synced)}"
        )
    else:
        print("No new history runs found to synchronize.")


if __name__ == "__main__":
    main()
