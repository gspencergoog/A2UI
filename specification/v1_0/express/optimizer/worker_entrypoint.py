"""Subagent worker execution entrypoint for A2UI Express optimizer loop.

Executed inside isolated branched workspaces. Loads reigning champion, generates
mutated specification/compiler code, overwrites workspace files, executes local
evaluation gauntlets, and computes the fitness score.
"""

import argparse
import json
import os
import sys
import unittest
from typing import Any

try:
    # pylint: disable=import-error
    from google import genai
except ImportError:
    genai = None

from specification.v1_0.express.optimizer.gauntlet import EvaluationGauntlet
from specification.v1_0.express.optimizer.manifest import Gene
from specification.v1_0.express.optimizer.mutator import ExpressMutator
# pylint: enable=import-error, wrong-import-position

SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_worker_gauntlet(
    parent_id: str, model_name: str = "gemini-3.5-flash", thinking_budget: int = 4096
) -> dict[str, Any]:
    """Executes mutation and evaluation gauntlet, returning completion payload."""
    leaderboard_path = os.path.join(SPEC_EXPRESS_DIR, "leaderboard.json")
    with open(leaderboard_path, "r", encoding="utf-8") as f:
        leaderboard = json.load(f)

    # Load reigning champion content from active workspace
    champion = Gene.load_baseline(SPEC_EXPRESS_DIR)
    champion.gene_id = leaderboard.get("reigning_champion", "gene_v1_0")

    prompt_path = os.path.join(SPEC_EXPRESS_DIR, "optimizer", "mutate_prompt.md")
    mutator = ExpressMutator(prompt_path, model_name=model_name, thinking_budget=thinking_budget)

    print(f"Generating mutation from parent {champion.gene_id} using {model_name} (budget: {thinking_budget})...")
    target_candidates_dir = os.path.abspath(os.path.join(SPEC_EXPRESS_DIR, "..", "..", "scratch", "candidates"))
    offspring = mutator.generate_mutation(champion, target_disk_dir=target_candidates_dir)

    if not offspring:
        return {"status": "error", "reason": "Mutation syntax self-repair failed"}

    # Execute 100% in-memory gauntlet evaluation without overwriting disk files
    gauntlet = EvaluationGauntlet()
    reigning_score = leaderboard.get("history", {}).get(champion.gene_id, {}).get("fitness_score", 0.85)
    score, metrics = gauntlet.evaluate_candidate(offspring, reigning_score)

    if score == 0.0:
        return {
            "candidate_id": offspring.gene_id,
            "status": "failed",
            "gate": metrics.get("gate_reached", "Evaluation Gauntlet"),
            "fitness_score": 0.0,
        }
    offspring.save_to_disk(target_candidates_dir)

    return {
        "candidate_id": offspring.gene_id,
        "parent_id": champion.gene_id,
        "status": "success",
        "fitness_score": offspring.fitness_score,
        "metrics": offspring.metrics,
        "artifacts_dir": os.path.join(target_candidates_dir, offspring.gene_id),
    }


def main():
    """Parses arguments and runs the worker evaluation gauntlet."""
    if genai is None:
        print("Error: 'google-genai' SDK not available in active Python environment. Short-circuiting worker.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="A2UI Express Subagent Worker Entrypoint")
    parser.add_argument("--parent_id", default="gene_v1_0", help="Parent champion ID")
    parser.add_argument("--model_name", default="gemini-3.5-flash", help="Target Gemini model identifier")
    parser.add_argument("--thinking_budget", type=int, default=4096, help="Scratchpad reasoning token allocation")
    args = parser.parse_args()

    payload = run_worker_gauntlet(args.parent_id, model_name=args.model_name, thinking_budget=args.thinking_budget)
    print("\n=== SUBAGENT COMPLETION PAYLOAD ===")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
