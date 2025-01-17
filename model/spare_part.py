import logging
from typing import Literal

# Set up logging for professional debugging and tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SparePart:
    """
    Represents a spare part in Techburg. Parts come in three sizes: small, medium, large.
    They provide different enhancements to survivor bots (+3%, +5%, or +7%) and corrode
    over time unless stored in a recharge station. When corroded to zero or consumed,
    they no longer offer enhancements. Scavenger swarms can consume them for energy.
    """

    def __init__(self, x: int, y: int, part_type: Literal["small", "medium", "large"]):
        """
        Initialize a spare part.

        Args:
            x (int): The x-coordinate of the part.
            y (int): The y-coordinate of the part.
            part_type (Literal["small", "medium", "large"]): The size/type of the part.
        """
        self.x = x
        self.y = y
        self.part_type = part_type

        # For console/ASCII display if desired
        self.symbol = "P"

        # Base enhancement (for SurvivorBots)
        if self.part_type == "small":
            self.enhancement_value = 3.0  # +3% for a bot
        elif self.part_type == "medium":
            self.enhancement_value = 5.0  # +5% for a bot
        elif self.part_type == "large":
            self.enhancement_value = 7.0  # +7% for a bot
        else:
            raise ValueError(f"Invalid part type: {self.part_type}")

        # Track maximum enhancement so we can recharge
        self.max_enhancement_value = self.enhancement_value

        # State flags
        self.is_in_station = False   # True if placed in a recharge station
        self.is_consumed = False     # True if a swarm has consumed this part

        logging.info(f"Spare part of type '{self.part_type}' created at ({self.x}, {self.y}) "
                     f"with enhancement {self.enhancement_value}%.")

    def update_corrosion(self) -> None:
        """
        Corrode the part by subtracting 0.1 from its current enhancement each simulation step.
        This happens only if the part is NOT in a station and NOT consumed.
        Enhancement cannot go below zero.
        """
        if not self.is_in_station and not self.is_consumed:
            self.enhancement_value -= 0.1
            if self.enhancement_value < 0:
                self.enhancement_value = 0
            logging.info(f"Part at ({self.x}, {self.y}) corroded to {self.enhancement_value:.1f}%.")

    def is_corroded(self) -> bool:
        """
        Check if the part's enhancement has dropped to 0 or below.

        Returns:
            bool: True if the part is effectively corroded away, False otherwise.
        """
        return self.enhancement_value <= 0

    def recharge(self) -> None:
        """
        If the part is in a recharge station and not consumed, it regains +0.1 each step
        until it reaches max_enhancement_value.
        """
        if self.is_in_station and not self.is_consumed:
            if self.enhancement_value < self.max_enhancement_value:
                old_value = self.enhancement_value
                self.enhancement_value += 0.1
                if self.enhancement_value > self.max_enhancement_value:
                    self.enhancement_value = self.max_enhancement_value
                logging.info(f"Part at ({self.x}, {self.y}) recharged from "
                             f"{old_value:.1f}% to {self.enhancement_value:.1f}%.")

    def consume_by_swarm(self) -> float:
        """
        Consumed by a scavenger swarm. Returns the energy boost:
          small -> +1%
          medium -> +2%
          large -> +3%

        Once consumed, the part is effectively removed (is_consumed = True).
        The simulation should remove it from the grid.

        Returns:
            float: The energy boost given to the swarm.
        """
        if self.is_consumed:
            logging.warning(f"Part at ({self.x}, {self.y}) already consumed.")
            return 0.0

        if self.part_type == "small":
            energy_boost = 1.0
        elif self.part_type == "medium":
            energy_boost = 2.0
        elif self.part_type == "large":
            energy_boost = 3.0
        else:
            raise ValueError(f"Invalid part type: {self.part_type}")

        self.is_consumed = True
        logging.info(f"Part at ({self.x}, {self.y}) consumed by swarm for +{energy_boost}% energy.")
        return energy_boost
