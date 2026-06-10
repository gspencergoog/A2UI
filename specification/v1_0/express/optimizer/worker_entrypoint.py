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

# Support direct execution from worktree root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

# pylint: disable=import-error, wrong-import-position
from specification.v1_0.express.optimizer.manifest import Gene
from specification.v1_0.express.optimizer.mutator import ExpressMutator
# pylint: enable=import-error, wrong-import-position

SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run_worker_gauntlet(parent_id: str) -> dict[str, Any]:
    """Executes mutation and evaluation gauntlet, returning completion payload."""
    leaderboard_path = os.path.join(SPEC_EXPRESS_DIR, "leaderboard.json")
    with open(leaderboard_path, "r", encoding="utf-8") as f:
        leaderboard = json.load(f)

    # Load reigning champion content from active workspace
    champion = Gene.load_baseline(SPEC_EXPRESS_DIR)
    champion.gene_id = leaderboard.get("reigning_champion", "gene_v1_0")

    prompt_path = os.path.join(SPEC_EXPRESS_DIR, "optimizer", "mutate_prompt.md")
    mutator = ExpressMutator(prompt_path)

    print(f"Generating mutation from parent {champion.gene_id}...")
    target_candidates_dir = os.path.abspath(os.path.join(SPEC_EXPRESS_DIR, "..", "..", "scratch", "candidates"))
    offspring = mutator.generate_mutation(champion, target_disk_dir=target_candidates_dir)

    if not offspring:
        return {"status": "error", "reason": "Mutation syntax self-repair failed"}

    # Overwrite local workspace sandbox compiler and decompiler files
    with open(os.path.join(SPEC_EXPRESS_DIR, "compiler.py"), "w", encoding="utf-8") as f:
        f.write(offspring.compiler_content)
    with open(os.path.join(SPEC_EXPRESS_DIR, "decompiler.py"), "w", encoding="utf-8") as f:
        f.write(offspring.decompiler_content)
    with open(os.path.join(SPEC_EXPRESS_DIR, "a2ui_express.md"), "w", encoding="utf-8") as f:
        f.write(offspring.a2ui_express_content)
    with open(os.path.join(SPEC_EXPRESS_DIR, "basic_prompt.md"), "w", encoding="utf-8") as f:
        f.write(offspring.basic_prompt_content)

    # Tier 0 & Tier 1 Evaluation Gate
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(SPEC_EXPRESS_DIR, pattern="test_express.py")
    test_result = unittest.TextTestRunner(verbosity=0).run(test_suite)

    if not test_result.wasSuccessful():
        return {
            "candidate_id": offspring.gene_id,
            "status": "failed",
            "gate": "Tier 0/1 Unit Tests",
            "fitness_score": 0.0,
        }

    # Compute Fitness Metrics
    verbose_json_base_tokens = 500  # Standard reference token count
    dsl_output_tokens = len(offspring.compiler_content.split()) // 10
    t_out = 1.0 - (dsl_output_tokens / verbose_json_base_tokens)

    max_prompt_budget = 1000
    prompt_tokens = len(offspring.basic_prompt_content.split())
    t_prompt = 1.0 - (prompt_tokens / max_prompt_budget)

    # Formula: F = (E * A) * [w_s*S + w_out*T_out + w_prompt*T_prompt - w_r*R]
    # Assuming E=1, A=1, S=1, R=0 for initial passing round-trip
    fitness = 0.35 * 1.0 + 0.35 * t_out + 0.15 * t_prompt - 0.15 * 0.0

    offspring.fitness_score = round(fitness, 4)
    offspring.metrics = {
        "output_compression": round(t_out, 4),
        "prompt_footprint_tokens": prompt_tokens,
        "compilation_success": True,
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
    parser = argparse.ArgumentParser(description="A2UI Express Subagent Worker Entrypoint")
    parser.add_argument("--parent_id", default="gene_v1_0", help="Parent champion ID")
    args = parser.parse_args()

    payload = run_worker_gauntlet(args.parent_id)
    print("\n=== SUBAGENT COMPLETION PAYLOAD ===")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
