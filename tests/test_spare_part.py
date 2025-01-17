import unittest
from model.spare_part import SparePart  # Correct import statement
import logging

# Disable logging during tests to avoid cluttering the output
logging.disable(logging.CRITICAL)


class TestSparePart(unittest.TestCase):
    def setUp(self):
        """Set up a spare part for testing."""
        self.small_part = SparePart(0, 0, "small")
        self.medium_part = SparePart(1, 1, "medium")
        self.large_part = SparePart(2, 2, "large")

    def test_initialization(self):
        """Test that spare parts are initialized correctly."""
        self.assertEqual(self.small_part.part_type, "small")
        self.assertEqual(self.small_part.enhancement_value, 3.0)
        self.assertEqual(self.small_part.max_enhancement_value, 3.0)
        self.assertFalse(self.small_part.is_in_station)
        self.assertFalse(self.small_part.is_consumed)

    def test_corrosion(self):
        """Test that spare parts corrode correctly when not in a station."""
        for _ in range(10):
            self.small_part.update_corrosion()
        self.assertAlmostEqual(self.small_part.enhancement_value, 2.0)

        for _ in range(20):
            self.small_part.update_corrosion()
        self.assertTrue(self.small_part.is_corroded())
        self.assertAlmostEqual(self.small_part.enhancement_value, 0.0)

    def test_recharge(self):
        """Test that spare parts recharge correctly when in a station."""
        for _ in range(10):
            self.medium_part.update_corrosion()
        self.assertAlmostEqual(self.medium_part.enhancement_value, 4.0)

        self.medium_part.is_in_station = True
        for _ in range(10):
            self.medium_part.recharge()
        self.assertAlmostEqual(self.medium_part.enhancement_value, 5.0)

    def test_consume_by_swarm(self):
        """Test that spare parts are consumed correctly by swarms."""
        energy_boost = self.small_part.consume_by_swarm()
        self.assertEqual(energy_boost, 1.0)
        self.assertTrue(self.small_part.is_consumed)

        energy_boost = self.medium_part.consume_by_swarm()
        self.assertEqual(energy_boost, 2.0)
        self.assertTrue(self.medium_part.is_consumed)

        energy_boost = self.large_part.consume_by_swarm()
        self.assertEqual(energy_boost, 3.0)
        self.assertTrue(self.large_part.is_consumed)

        energy_boost = self.small_part.consume_by_swarm()
        self.assertEqual(energy_boost, 0.0)

    def test_invalid_part_type(self):
        """Test that an invalid part type raises a ValueError."""
        with self.assertRaises(ValueError):
            SparePart(0, 0, "invalid_type")


if __name__ == "__main__":
    unittest.main()