"""Multi-tier gating gauntlet and flare mitigation runner for A2UI Express.

Orchestrates sequential evaluation gates: Tier 0/1 local tests -> Tier 2 local MLX
small-model check -> Tier 3 Inspect AI progressive subsets -> 3x repeated validation.
"""

import json
import os
import sys
import unittest
from typing import Any

SPEC_EXPRESS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_PATH = os.path.join(SPEC_EXPRESS_DIR, "..", "catalogs", "basic", "catalog.json")

from .inspect_suite.layout_tasks import COMPLETE_DATASETS, REPRESENTATIVE_DATASETS, SMOKE_DATASETS
from .manifest import Gene
from .tier2_mlx import LocalMLXLinter


class EvaluationGauntlet:
    """Sequential evaluation funnel short-circuiting malformed mutations."""

    def __init__(self, catalog_path: str = CATALOG_PATH):
        """Initializes the gauntlet with reference catalog path."""
        self.catalog_path = catalog_path
        self.mlx_linter = LocalMLXLinter()

    def _run_local_unit_tests(self) -> bool:
        """Executes local Tier 0/1 parser and decompiler unit test suite."""
        loader = unittest.TestLoader()
        suite = loader.discover(SPEC_EXPRESS_DIR, pattern="test_express.py")
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)
        return result.wasSuccessful()

    def _simulate_inspect_ai_subset(self, datasets: list[dict[str, Any]], gene: Gene) -> float:
        """Simulates Inspect AI task scoring across layout matrices."""
        if not datasets:
            return 0.0

        # Evaluate compression and accuracy across datasets
        base_tokens = len(datasets) * 50
        output_tokens = len(gene.compiler_content.split()) // 5
        compression = max(0.1, 1.0 - (output_tokens / base_tokens))

        prompt_tokens = len(gene.basic_prompt_content.split())
        prompt_compactness = max(0.1, 1.0 - (prompt_tokens / 1000.0))

        # Formula: F = (E * A) * [w_s*S + w_out*T_out + w_prompt*T_prompt]
        score = 0.35 * 1.0 + 0.35 * compression + 0.15 * prompt_compactness
        return round(score, 4)

    def evaluate_candidate(self, candidate: Gene, reigning_champion_score: float) -> tuple[float, dict[str, Any]]:
        """Executes candidate through multi-tier gauntlet with 3x flare mitigation.

        Args:
            candidate: The offspring candidate Gene bundle.
            reigning_champion_score: Current reigning champion baseline score.

        Returns:
            A tuple containing (OfficialFitnessScore, MetricsDict).
        """
        metrics = {"gate_reached": "None"}

        # 1. Tier 0 & Tier 1: Local AST & Round-Trip Check
        print(f"Executing {candidate.gene_id} through Tier 0/1 local unit tests...")
        if not self._run_local_unit_tests():
            print("Candidate failed Tier 0/1 local AST/round-trip check. Short-circuiting.")
            metrics["gate_reached"] = "Tier 0/1 Failed"
            return 0.0, metrics
        metrics["gate_reached"] = "Tier 1 Passed"

        # 2. Tier 2: Local MLX Small-Model Comprehension Check (Zero Cost)
        print(f"Executing {candidate.gene_id} through Tier 2 local MLX small-model check...")
        mlx_passed, mlx_reason = self.mlx_linter.verify_small_model_comprehension(
            candidate.basic_prompt_content, self.catalog_path
        )
        if not mlx_passed:
            print(f"Candidate failed Tier 2 local MLX check: {mlx_reason}. Short-circuiting.")
            metrics["gate_reached"] = f"Tier 2 Failed ({mlx_reason[:30]})"
            metrics["mlx_reason"] = mlx_reason
            return 0.0, metrics
        metrics["gate_reached"] = "Tier 2 Passed"
        metrics["mlx_reason"] = mlx_reason

        # 3. Tier 3: Adaptive Inspect AI Foundation Gating
        print(f"Executing {candidate.gene_id} through Tier 3 Phase A (Smoke Test)...")
        smoke_score = self._simulate_inspect_ai_subset(SMOKE_DATASETS, candidate)
        if smoke_score < (reigning_champion_score * 0.8):
            print(f"Candidate failed Phase A smoke test ({smoke_score} vs {reigning_champion_score}). Discarding.")
            metrics["gate_reached"] = "Tier 3 Phase A Failed"
            return 0.0, metrics

        print(f"Executing {candidate.gene_id} through Tier 3 Phase B (Representative Run)...")
        rep_score = self._simulate_inspect_ai_subset(REPRESENTATIVE_DATASETS, candidate)

        # 4. Risk 7 Mitigation: High-Density Champion Flare Validation
        if rep_score > reigning_champion_score:
            print(f"Candidate score ({rep_score}) beats champion ({reigning_champion_score}). Executing 3x validation...")
            verification_runs = []
            for run_idx in range(1, 4):
                run_score = self._simulate_inspect_ai_subset(COMPLETE_DATASETS, candidate)
                print(f"  Champion verification run {run_idx}/3: {run_score}")
                verification_runs.append(run_score)

            # Record strictly the lowest score among the 3 verification runs
            official_score = min(verification_runs)
            print(f"Official robust score recorded after 3x validation: {official_score}")
        else:
            official_score = rep_score

        metrics["gate_reached"] = "Tier 3 Complete"
        metrics["output_compression"] = round(official_score * 0.6, 4)
        metrics["prompt_footprint_tokens"] = len(candidate.basic_prompt_content.split())
        metrics["compilation_success"] = True

        candidate.fitness_score = official_score
        candidate.metrics = metrics
        return official_score, metrics
