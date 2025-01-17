import unittest
from model.grid import Grid
from model.survivor_bot import SurvivorBot, BotType
from model.malfunctioning_drone import MalfunctioningDrone

class TestMalfunctioningDrone(unittest.TestCase):
    def setUp(self):
        """Set up a grid and entities for testing."""
        self.grid = Grid(width=10, height=10)
        self.drone = MalfunctioningDrone(x=5, y=5, energy=100.0, detection_range=3)
        self.grid.add_entity(5, 5, self.drone)

    def test_initialization(self):
        """Test the initialization of the MalfunctioningDrone."""
        self.assertEqual(self.drone.x, 5)
        self.assertEqual(self.drone.y, 5)
        self.assertEqual(self.drone.energy, 100.0)
        self.assertEqual(self.drone.detection_range, 3)
        self.assertFalse(self.drone.hibernating)

    def test_detect_bots(self):
        """Test the detect_bots method."""
        bot1 = SurvivorBot(x=6, y=5, bot_type=BotType.REPAIR)
        bot2 = SurvivorBot(x=8, y=5, bot_type=BotType.SCOUT)
        self.grid.add_entity(6, 5, bot1)
        self.grid.add_entity(8, 5, bot2)

        # Bot1 is within detection range, bot2 is not
        nearest_bot = self.drone.detect_bots([bot1, bot2])
        self.assertEqual(nearest_bot, bot1)

    def test_move_toward(self):
        """Test the move_toward method."""
        bot = SurvivorBot(x=7, y=5, bot_type=BotType.REPAIR)
        self.grid.add_entity(7, 5, bot)

        # Move toward the bot
        self.drone.move_toward(bot.x, bot.y, self.grid)
        self.assertEqual(self.drone.x, 6)
        self.assertEqual(self.drone.y, 5)

    def test_attack_repair_bot(self):
        """Test the attack method on a repair bot."""
        bot = SurvivorBot(x=5, y=5, bot_type=BotType.REPAIR)
        self.grid.add_entity(5, 5, bot)

        # Attack the bot
        self.drone.attack(bot)
        self.assertEqual(bot.energy, 0)

    def test_attack_non_repair_bot(self):
        """Test the attack method on a non-repair bot."""
        bot = SurvivorBot(x=5, y=5, bot_type=BotType.SCOUT)
        self.grid.add_entity(5, 5, bot)

        # Attack the bot
        self.drone.attack(bot)
        self.assertLess(bot.energy, 100)  # Energy should be reduced

    def test_recharge(self):
        """Test the recharge method."""
        self.drone.energy = 15  # Set energy to <= 20 to trigger hibernation
        self.drone.recharge()

        # Drone should be hibernating and recharging
        self.assertTrue(self.drone.hibernating)
        self.assertGreater(self.drone.energy, 15)

        # Recharge until energy >= 100
        while self.drone.energy < 100:
            self.drone.recharge()
        self.assertFalse(self.drone.hibernating)
        self.assertEqual(self.drone.energy, 100.0)

    def test_update_hibernation(self):
        """Test the update method when the drone is hibernating."""
        self.drone.energy = 15  # Set energy to <= 20 to trigger hibernation
        self.drone.update(self.grid, [])

        # Drone should be hibernating and recharging
        self.assertTrue(self.drone.hibernating)
        self.assertGreater(self.drone.energy, 15)

    def test_update_pursuit(self):
        """Test the update method when the drone is pursuing a bot."""
        bot = SurvivorBot(x=6, y=5, bot_type=BotType.SCOUT)
        self.grid.add_entity(6, 5, bot)

        # Drone should move toward the bot and attack
        self.drone.update(self.grid, [bot])
        self.assertEqual(self.drone.x, 6)
        self.assertEqual(self.drone.y, 5)
        self.assertLess(bot.energy, 100)  # Bot should be attacked

if __name__ == "__main__":
    unittest.main()