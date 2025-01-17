import unittest
import logging
from model.grid import Grid
from model.survivor_bot import SurvivorBot, BotType, SparePart, RechargeStation

class TestSurvivorBot(unittest.TestCase):
    def setUp(self):
        """Set up a grid and entities for testing."""
        self.grid = Grid(width=10, height=10)
        self.bot = SurvivorBot(x=5, y=5, bot_type=BotType.GATHERER, energy=100)
        self.grid.add_entity(5, 5, self.bot)

    def test_initialization(self):
        """Test the initialization of the SurvivorBot."""
        self.assertEqual(self.bot.x, 5)
        self.assertEqual(self.bot.y, 5)
        self.assertEqual(self.bot.bot_type, BotType.GATHERER)
        self.assertEqual(self.bot.energy, 100)
        self.assertFalse(self.bot.has_part)
        self.assertTrue(self.bot.is_active)

    def test_move_to(self):
        """Test the move_to method."""
        # Move to a valid position
        self.assertTrue(self.bot.move_to(6, 5, self.grid))
        self.assertEqual(self.bot.x, 6)
        self.assertEqual(self.bot.y, 5)
        self.assertEqual(self.bot.energy, 95)

        # Move to an invalid position (out of bounds)
        self.assertFalse(self.bot.move_to(10, 10, self.grid))
        self.assertEqual(self.bot.x, 6)
        self.assertEqual(self.bot.y, 5)

    def test_move_toward(self):
        """Test the move_toward method."""
        # Ensure bot can move toward a target position
        self.bot.energy = 100  # Ensure sufficient energy
        self.assertTrue(self.bot.move_toward(7, 5, self.grid, simulation_step=2))
        self.assertEqual(self.bot.x, 6)
        self.assertEqual(self.bot.y, 5)

    def test_detect_and_collect_part(self):
        """Test the detect_and_collect_part method."""
        part = SparePart(size="small")
        self.grid.add_entity(6, 5, part)

        # Detect and collect the part
        self.bot.detect_and_collect_part(self.grid)
        self.assertTrue(self.bot.has_part)
        self.assertEqual(self.bot.carried_part, part)

    def test_deposit_part(self):
        """Test the deposit_part method."""
        part = SparePart(size="small")
        self.bot.carried_part = part
        self.bot.has_part = True

        station = RechargeStation()
        self.grid.add_entity(5, 5, station)

        # Deposit the part at the station
        self.bot.deposit_part(self.grid)
        self.assertFalse(self.bot.has_part)
        self.assertIsNone(self.bot.carried_part)
        self.assertIn(part, station.stored_parts)

    def test_rest_or_consume_parts(self):
        """Test the rest_or_consume_parts method."""
        station = RechargeStation()
        self.grid.add_entity(5, 5, station)

        # Rest and recharge energy
        self.bot.energy = 90
        self.bot.rest_or_consume_parts(self.grid)
        self.assertEqual(self.bot.energy, 91)

        # Consume part immediately
        part = SparePart(size="small")
        self.bot.carried_part = part
        self.bot.has_part = True
        self.bot.energy = 4  # Below critical threshold
        self.bot.rest_or_consume_parts(self.grid)
        self.assertEqual(self.bot.energy, 14)
        self.assertFalse(self.bot.has_part)

    def test_handle_inactive_removal(self):
        """Test the handle_inactive_removal method."""
        self.bot.is_active = False
        self.bot.steps_inactive = 4

        # Handle inactive removal
        self.bot.handle_inactive_removal(self.grid)
        self.assertEqual(self.bot.steps_inactive, 5)

        # Remove the bot after 5 steps of inactivity
        self.bot.handle_inactive_removal(self.grid)
        self.assertIsNone(self.grid.get_entity(5, 5))

    def test_upgrade_ability(self):
        """Test the upgrade_ability method."""
        # Upgrade speed
        self.bot.upgrade_ability("speed", 50)
        self.assertEqual(self.bot.speed_enhancement, 50)

        # Upgrade vision
        self.bot.upgrade_ability("vision", 100)
        self.assertEqual(self.bot.vision_enhancement, 100)

        # Upgrade energy capacity
        self.bot.upgrade_ability("energy", 20)
        self.assertEqual(self.bot.energy_capacity, 120)

    def test_share_information(self):
        """Test the share_information method."""
        other_bot = SurvivorBot(x=6, y=5, bot_type=BotType.GATHERER, energy=100)
        self.grid.add_entity(6, 5, other_bot)

        # Share information
        self.bot.known_parts.add((7, 7))
        self.bot.share_information(other_bot)
        self.assertIn((7, 7), other_bot.known_parts)

    def test_transfer_energy(self):
        """Test the transfer_energy method."""
        # Create another bot with zero energy
        other_bot = SurvivorBot(x=6, y=5, bot_type=BotType.GATHERER, energy=0)
        self.grid.add_entity(6, 5, other_bot)

        # Debug entity placement
        placed_bot = self.grid.get_entity(6, 5)
        logging.info(f"Bot placed at (6, 5): {placed_bot}")

        # Ensure the bot has sufficient energy for transfer
        self.bot.energy = 100

        # Transfer energy
        self.bot.transfer_energy(other_bot)

        # Verify energy levels after transfer
        self.assertEqual(self.bot.energy, 80)  # Source bot loses 20 energy
        self.assertEqual(other_bot.energy, 20)  # Target bot gains 20 energy
        self.assertTrue(other_bot.is_active)  # Target bot becomes active

    def test_replicate_bot(self):
        """Test the replicate_bot method."""
        other_bot = SurvivorBot(x=5, y=5, bot_type=BotType.REPAIR, energy=100)
        self.grid.add_entity(5, 5, other_bot)

        station = RechargeStation()
        self.grid.add_entity(5, 5, station)

        # Replicate a new bot
        new_bot = self.bot.replicate_bot(other_bot, self.grid)
        if new_bot:
            self.assertIsInstance(new_bot, SurvivorBot)
            self.assertEqual(new_bot.x, 5)
            self.assertEqual(new_bot.y, 5)

if __name__ == "__main__":
    unittest.main()
