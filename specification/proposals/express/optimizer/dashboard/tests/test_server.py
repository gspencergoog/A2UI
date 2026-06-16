"""Unit tests verifying DashboardAPIHandler REST data structures."""

import unittest
from unittest.mock import MagicMock, patch
from ..server import DashboardAPIHandler


class TestDashboardServer(unittest.TestCase):
    """Verifies REST API helper return dictionary structures."""

    def test_get_leaderboard_data_fallback(self):
        """Verifies missing leaderboard cleanly returns default baseline structure."""
        with patch("os.path.exists", return_value=False):
            handler = DashboardAPIHandler.__new__(DashboardAPIHandler)
            data = handler._get_leaderboard_data()
            self.assertEqual(data["reigning_champion"], "gene_v1_0")

    def test_get_system_state_offline(self):
        """Verifies connection refusal cleanly sets mlx_online False."""
        with patch("socket.create_connection", side_effect=ConnectionRefusedError):
            handler = DashboardAPIHandler.__new__(DashboardAPIHandler)
            state = handler._get_system_state()
            self.assertFalse(state["mlx_online"])


if __name__ == "__main__":
    unittest.main()
