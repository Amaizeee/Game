from datetime import timedelta
import unittest

from random_number_game import SovereignDuration, TheGridGame


class TheGridGameTests(unittest.TestCase):
    def test_movement_discovers_and_captures_cells(self):
        game = TheGridGame(size=5)
        starting_xp = game.player.xp

        result = game.move("east")

        self.assertIn("Moved to (3, 2)", result)
        self.assertGreater(game.player.xp, starting_xp)
        self.assertEqual(game.cells[(3, 2)].team, game.player.team)
        self.assertIn((3, 2), game.player.discovered)

    def test_sovereign_cell_blocks_enemy_capture_until_expiry(self):
        game = TheGridGame(size=5)
        position = (game.player.x, game.player.y)
        game.buy_current_cell(SovereignDuration.DAY)

        game.player.name = "Rival"
        game.player.team = "violet"
        game.capture_current_position()

        self.assertEqual(game.cells[position].team, "cyan")
        self.assertEqual(game.cells[position].sovereign_owner, "Neon Runner")

        game.now += timedelta(days=2)
        game.capture_current_position()

        self.assertEqual(game.cells[position].team, "violet")
        self.assertEqual(game.cells[position].captured_by, "Rival")

    def test_state_payload_supports_web_preview(self):
        game = TheGridGame(size=5)

        state = game.state_payload()

        self.assertEqual(state["size"], 5)
        self.assertEqual(state["player"]["team"], "cyan")
        self.assertEqual(len(state["cells"]), 25)
        self.assertIn("leaderboard", state)

    def test_leaderboard_reports_mayor_and_dominant_team(self):
        game = TheGridGame(size=5)

        leaderboard = game.leaderboard()

        self.assertIn("Mayor: Neon Runner", leaderboard)
        self.assertIn("Dominant team: Bleu Cyan", leaderboard)


if __name__ == "__main__":
    unittest.main()
