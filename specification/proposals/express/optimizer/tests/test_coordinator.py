"""Unit tests verifying EvolutionCoordinator file locking and champion selection."""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch
from ..coordinator import EvolutionCoordinator


class TestEvolutionCoordinator(unittest.TestCase):
    """Verifies atomic write-locking and leaderboard score gating."""

    def setUp(self):
        """Creates a temporary file system sandbox and mock leaderboard."""
        self.test_dir = tempfile.mkdtemp()
        self.leaderboard_path = os.path.join(self.test_dir, "leaderboard.json")

        initial_board = {
            "reigning_champion": "gene_base",
            "history": {
                "gene_base": {
                    "parent": None,
                    "fitness_score": 0.85,
                    "metrics": {"compression": 0.5},
                }
            },
        }
        with open(self.leaderboard_path, "w", encoding="utf-8") as f:
            json.dump(initial_board, f, indent=2)

        self.coord = EvolutionCoordinator(self.leaderboard_path)

    def tearDown(self):
        """Cleans up temporary files."""
        shutil.rmtree(self.test_dir)

    def test_read_leaderboard_locked(self):
        """Verifies acquiring shared lock cleanly reads central registry."""
        data = self.coord.read_leaderboard_locked()
        self.assertEqual(data["reigning_champion"], "gene_base")

    @patch("specification.v1_0.express.optimizer.coordinator.Gene.load_from_disk")
    @patch("specification.v1_0.express.optimizer.coordinator.EvaluationGauntlet.evaluate_candidate")
    def test_record_champion_locked_rejection(self, mock_eval, mock_load):
        """Verifies lower fitness scores or failed runs are discarded."""
        mock_eval.return_value = (0.80, {"gate_reached": "Tier 3 Complete"})
        inferior_payload = {
            "candidate_id": "gene_inferior",
            "parent_id": "gene_base",
            "status": "success",
            "fitness_score": 0.80,
            "artifacts_dir": "/path/to/artifacts",
        }
        recorded = self.coord.record_champion_locked(inferior_payload)
        self.assertFalse(recorded)

        board = self.coord.read_leaderboard_locked()
        self.assertEqual(board["reigning_champion"], "gene_base")
        self.assertNotIn("gene_inferior", board["history"])

    @patch("specification.v1_0.express.optimizer.coordinator.Gene.load_from_disk")
    @patch("specification.v1_0.express.optimizer.coordinator.EvaluationGauntlet.evaluate_candidate")
    def test_record_champion_locked_success(self, mock_eval, mock_load):
        """Verifies candidate achieving higher fitness score atomically unseats champion."""
        mock_eval.return_value = (0.95, {"compression": 0.7})
        superior_payload = {
            "candidate_id": "gene_superior",
            "parent_id": "gene_base",
            "status": "success",
            "fitness_score": 0.95,
            "metrics": {"compression": 0.7},
            "artifacts_dir": "/path/to/artifacts",
        }
        recorded = self.coord.record_champion_locked(superior_payload)
        self.assertTrue(recorded)

        board = self.coord.read_leaderboard_locked()
        self.assertEqual(board["reigning_champion"], "gene_superior")
        self.assertIn("gene_superior", board["history"])
        self.assertEqual(board["history"]["gene_superior"]["fitness_score"], 0.95)


if __name__ == "__main__":
    unittest.main()
