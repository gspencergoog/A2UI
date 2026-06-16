"""Unit tests verifying EvaluationGauntlet sequential gating and flare mitigation."""

import unittest
from unittest.mock import MagicMock, patch
from ..gauntlet import EvaluationGauntlet
from ..manifest import Gene


class TestEvaluationGauntlet(unittest.TestCase):
    """Verifies token-saving short-circuits and 3x repeated verification runs."""

    def setUp(self):
        """Initializes gauntlet and dummy candidate gene."""
        self.gauntlet = EvaluationGauntlet("/dummy/catalog.json")
        self.candidate = Gene(
            gene_id="gene_test",
            a2ui_express_content="# Spec",
            basic_prompt_content="Prompt",
            compiler_content="x = 1",
            decompiler_content="y = 2",
        )

    @patch.object(EvaluationGauntlet, "_run_local_unit_tests", return_value=False)
    def test_evaluate_candidate_tier1_short_circuit(self, mock_unit_tests):
        """Verifies candidate failing local Tier 0/1 unit tests short-circuits immediately."""
        score, metrics = self.gauntlet.evaluate_candidate(self.candidate, reigning_champion_score=0.85)
        self.assertEqual(score, 0.0)
        self.assertEqual(metrics["gate_reached"], "Tier 0/1 Failed")

    @patch.object(EvaluationGauntlet, "_run_local_unit_tests", return_value=True)
    def test_evaluate_candidate_tier2_mlx_short_circuit(self, mock_unit_tests):
        """Verifies candidate failing local MLX comprehension short-circuits at zero API cost."""
        self.gauntlet.mlx_linter.verify_small_model_comprehension = MagicMock(
            return_value=(False, "MLX socket connection refused")
        )
        score, metrics = self.gauntlet.evaluate_candidate(self.candidate, reigning_champion_score=0.85)
        self.assertEqual(score, 0.0)
        self.assertIn("Tier 2 Failed", metrics["gate_reached"])

    @patch.object(EvaluationGauntlet, "_run_local_unit_tests", return_value=True)
    def test_evaluate_candidate_tier3_flare_mitigation(self, mock_unit_tests):
        """Verifies candidate achieving champion score triggers 3x repeated validation."""
        self.gauntlet.mlx_linter.verify_small_model_comprehension = MagicMock(
            return_value=(True, "Successfully parsed MLX line")
        )

        # Mock progressive subset simulation scores
        # Smoke score: 0.90 -> Representative score: 0.95 (beats 0.85 champion)
        # 3x Verification runs: [0.94, 0.92, 0.96] -> Official recorded score must be min(0.92)
        with patch.object(EvaluationGauntlet, "_simulate_inspect_ai_subset", side_effect=[0.90, 0.95, 0.94, 0.92, 0.96]):
            score, metrics = self.gauntlet.evaluate_candidate(self.candidate, reigning_champion_score=0.85)
            self.assertEqual(score, 0.92)
            self.assertEqual(metrics["gate_reached"], "Tier 3 Complete")
            self.assertEqual(self.candidate.fitness_score, 0.92)


if __name__ == "__main__":
    unittest.main()
