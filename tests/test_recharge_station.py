import unittest
from model.recharge_station import RechargeStation
from model.spare_part import SparePart
from model.survivor_bot import SurvivorBot, BotType
import logging

# Disable logging during tests to avoid cluttering the output
logging.disable(logging.CRITICAL)


class TestRechargeStation(unittest.TestCase):
    def setUp(self):
        """Set up a recharge station and some spare parts/bots for testing."""
        self.station = RechargeStation(0, 0, capacity=5)
        self.part1 = SparePart(1, 1, "small")
        self.part2 = SparePart(2, 2, "medium")
        self.part3 = SparePart(3, 3, "large")
        self.bot1 = SurvivorBot(0, 0, BotType.GATHERER)
        self.bot2 = SurvivorBot(1, 1, BotType.REPAIR)

    def test_initialization(self):
        """Test that the recharge station is initialized correctly."""
        self.assertEqual(self.station.x, 0)
        self.assertEqual(self.station.y, 0)
        self.assertEqual(self.station.capacity, 5)
        self.assertEqual(len(self.station.stored_parts), 0)
        self.assertEqual(len(self.station.bots), 0)

    def test_store_part(self):
        """Test storing parts in the recharge station."""
        self.assertTrue(self.station.store_part(self.part1))
        self.assertEqual(len(self.station.stored_parts), 1)
        self.assertTrue(self.part1.is_in_station)

        self.assertTrue(self.station.store_part(self.part2))
        self.assertEqual(len(self.station.stored_parts), 2)

        # Test storing beyond capacity
        for _ in range(3):
            self.station.store_part(SparePart(0, 0, "small"))
        self.assertFalse(self.station.store_part(self.part3))  # Should fail

    def test_consume_part(self):
        """Test consuming parts from the recharge station."""
        self.station.store_part(self.part1)
        self.station.store_part(self.part2)

        consumed_part = self.station.consume_part()
        self.assertEqual(consumed_part, self.part1)
        self.assertEqual(len(self.station.stored_parts), 1)

        consumed_part = self.station.consume_part()
        self.assertEqual(consumed_part, self.part2)
        self.assertEqual(len(self.station.stored_parts), 0)

        # Test consuming when no parts are available
        consumed_part = self.station.consume_part()
        self.assertIsNone(consumed_part)

    def test_recharge_parts(self):
        """Test recharging parts in the recharge station."""
        self.part1.enhancement_value = 1.0  # Corrode the part
        self.station.store_part(self.part1)
        self.station.recharge_parts()
        self.assertAlmostEqual(self.part1.enhancement_value, 1.1)

    def test_add_bot(self):
        """Test adding bots to the recharge station."""
        self.assertTrue(self.station.add_bot(self.bot1))
        self.assertEqual(len(self.station.bots), 1)

        self.assertTrue(self.station.add_bot(self.bot2))
        self.assertEqual(len(self.station.bots), 2)

        # Test adding beyond capacity
        for _ in range(3):
            self.station.add_bot(SurvivorBot(0, 0, BotType.GATHERER))
        self.assertFalse(self.station.add_bot(SurvivorBot(0, 0, BotType.REPAIR)))  # Should fail

    def test_remove_bot(self):
        """Test removing bots from the recharge station."""
        self.station.add_bot(self.bot1)
        self.station.add_bot(self.bot2)

        self.station.remove_bot(self.bot1)
        self.assertEqual(len(self.station.bots), 1)

        self.station.remove_bot(self.bot2)
        self.assertEqual(len(self.station.bots), 0)

        # Test removing a bot that is not in the station
        self.station.remove_bot(self.bot1)  # Should log a warning

    def test_share_information(self):
        """Test sharing information among bots in the recharge station."""
        self.station.add_bot(self.bot1)
        self.station.add_bot(self.bot2)

        # Add some known parts to each bot
        self.bot1.known_parts.add((1, 1))
        self.bot2.known_parts.add((2, 2))

        self.station.share_information()
        self.assertEqual(len(self.bot1.known_parts), 2)
        self.assertEqual(len(self.bot2.known_parts), 2)

    def test_can_replicate(self):
        """Test if the station can replicate a bot."""
        self.assertFalse(self.station.can_replicate())  # Not enough parts

        self.station.store_part(self.part1)
        self.station.store_part(self.part2)
        self.station.store_part(self.part3)
        self.assertTrue(self.station.can_replicate())

    def test_replicate_bot(self):
        """Test replicating a bot."""
        # Add enough parts and bots for replication
        self.station.store_part(self.part1)
        self.station.store_part(self.part2)
        self.station.store_part(self.part3)
        self.station.add_bot(self.bot1)
        self.station.add_bot(self.bot2)

        # Replicate a bot (random, so may fail)
        new_bot = self.station.replicate_bot()
        if new_bot:
            self.assertIn(new_bot.bot_type, [BotType.GATHERER, BotType.REPAIR])
            self.assertEqual(len(self.station.stored_parts), 0)  # Parts consumed


if __name__ == "__main__":
    unittest.main()