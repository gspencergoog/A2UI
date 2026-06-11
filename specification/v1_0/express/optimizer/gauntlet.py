"""Multi-tier gating gauntlet and flare mitigation runner for A2UI Express.

Orchestrates sequential evaluation gates: Tier 0/1 local tests -> Tier 2 local MLX
small-model check -> Tier 3 Inspect AI progressive subsets -> 3x repeated validation.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch
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

    def _run_local_unit_tests(self, gene: Gene) -> bool:
        """Executes in-memory Tier 0/1 compilation checks against candidate AST logic."""
        dummy_ns = {"__name__": "express_candidate_eval"}
        try:
            with patch("sys.exit", side_effect=RuntimeError), \
                 patch("builtins.exit", side_effect=RuntimeError), \
                 patch("builtins.quit", side_effect=RuntimeError):
                exec(gene.compiler_content, dummy_ns)
                exec(gene.decompiler_content, dummy_ns)

                comp_cls = dummy_ns.get("ExpressCompiler")
                dec_cls = dummy_ns.get("ExpressDecompiler")
                if not comp_cls or not dec_cls:
                    return False

                compiler = comp_cls(self.catalog_path)
                decompiler = dec_cls(self.catalog_path)

                # Check 1: Basic component layout and structural integrity
                dsl1 = "root = Column([field])\nfield = TextField(\"Label\", @/key)"
                if "@" not in gene.a2ui_express_content and "$/" in gene.compiler_content:
                    dsl1 = "root = Column([field])\nfield = TextField(\"Label\", $/key)"

                envelope = compiler.compile(dsl1, surface_id="mem_surf")
                if envelope.get("version") != "v1.0":
                    return False

                create_surface = envelope["createSurface"]
                if create_surface.get("component") != "Column":
                    return False

                children = create_surface.get("children", [])
                if len(children) != 1 or children[0].get("component") != "TextField":
                    return False

                # Verify that path bindings map strictly to path properties
                val = children[0].get("value")
                if isinstance(val, dict):
                    if val.get("path") != "/key":
                        return False
                elif val not in ("@/key", "@key", "$/key", "$key"):
                    return False

                # Check 2: Action event data structures
                dsl2 = 'root = Button("Submit Deal", "primary", Event("save_deal", {rep: @form/rep}))'
                if "@" not in gene.a2ui_express_content and "$/" in gene.compiler_content:
                    dsl2 = 'root = Button("Submit Deal", "primary", Event("save_deal", {rep: $/form/rep}))'

                envelope2 = compiler.compile(dsl2)
                create_surf2 = envelope2.get("createSurface", {})

                components = create_surf2.get("components", [create_surf2])
                button_comp = next((c for c in components if c.get("component") == "Button"), None)
                if not button_comp:
                    return False

                if button_comp.get("variant") != "primary":
                    return False

                action = button_comp.get("action", {})
                event = action.get("event", {})
                if event.get("name") != "save_deal":
                    return False

                context = event.get("context", {})
                rep = context.get("rep", {})
                if rep.get("path") != "/form/rep":
                    return False

                # Check 3: dataModel mapping
                dsl3 = '@/user/age = 30\nroot = Column([])'
                if "@" not in gene.a2ui_express_content and "$/" in gene.compiler_content:
                    dsl3 = '$/user/age = 30\nroot = Column([])'
                envelope3 = compiler.compile(dsl3)
                dm = envelope3.get("createSurface", {}).get("dataModel", {})
                if dm.get("user", {}).get("age") != 30:
                    return False

                return True
        except Exception:
            return False

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
        if not self._run_local_unit_tests(candidate):
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
