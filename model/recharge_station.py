from __future__ import annotations  # Enable postponed evaluation of annotations
import logging
import random
from typing import List, Optional
from model.spare_part import SparePart
from model.survivor_bot import SurvivorBot, BotType

# Set up logging for professional debugging and tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RechargeStation:
    """
    Represents a recharge station in Techburg.
    Handles bot recharging, part storage, and bot replication.
    """

    def __init__(self, x: int, y: int, capacity: int = 5):
        """
        Initialize a recharge station.

        Args:
            x (int): The x-coordinate of the station.
            y (int): The y-coordinate of the station.
            capacity (int): The maximum number of bots the station can hold (default: 5).
        """
        self.x = x
        self.y = y
        self.capacity = capacity
        self.stored_parts: List[SparePart] = []  # Parts stored for bots
        self.bots: List[SurvivorBot] = []  # Bots currently occupying the station
        self.symbol = "S"  # GUI representation
        logging.info(f"Recharge station created at ({self.x}, {self.y}).")

    # -------------------------------------------------------------------------
    # Part Management
    # -------------------------------------------------------------------------
    def store_part(self, part: SparePart) -> bool:
        """
        Stores a spare part at the recharge station.

        Args:
            part (SparePart): The part to store.

        Returns:
            bool: True if the part was stored, False otherwise.
        """
        if len(self.stored_parts) < self.capacity:
            self.stored_parts.append(part)
            part.is_in_station = True  # Part stops corroding and starts recharging
            logging.info(f"Part stored at station ({self.x}, {self.y}). Current parts: {len(self.stored_parts)}")
            return True
        else:
            logging.warning(f"Station at ({self.x}, {self.y}) is full. Cannot store more parts.")
            return False

    def consume_part(self) -> Optional[SparePart]:
        """
        Removes and returns a stored part for consumption by a bot.

        Returns:
            Optional[SparePart]: The consumed part, or None if no parts are available.
        """
        if self.stored_parts:
            part = self.stored_parts.pop(0)
            logging.info(f"Part consumed at station ({self.x}, {self.y}). Remaining parts: {len(self.stored_parts)}")
            return part
        else:
            logging.warning(f"No parts available at station ({self.x}, {self.y}).")
            return None

    def recharge_parts(self) -> None:
        """
        Recharges all stored parts to their maximum enhancement values.
        """
        for part in self.stored_parts:
            part.recharge()
        logging.info(f"Parts at station ({self.x}, {self.y}) are recharging.")

    # -------------------------------------------------------------------------
    # Bot Management
    # -------------------------------------------------------------------------
    def add_bot(self, bot: SurvivorBot) -> bool:
        """
        Adds a bot to the station if capacity allows.

        Args:
            bot (SurvivorBot): The bot to add.

        Returns:
            bool: True if the bot was added, False otherwise.
        """
        if len(self.bots) < self.capacity:
            self.bots.append(bot)
            logging.info(f"Bot added to station ({self.x}, {self.y}). Current bots: {len(self.bots)}")
            return True
        else:
            logging.warning(f"Station at ({self.x}, {self.y}) is full. Cannot add more bots.")
            return False

    def remove_bot(self, bot: SurvivorBot) -> None:
        """
        Removes a bot from the station.

        Args:
            bot (SurvivorBot): The bot to remove.
        """
        if bot in self.bots:
            self.bots.remove(bot)
            logging.info(f"Bot removed from station ({self.x}, {self.y}). Current bots: {len(self.bots)}")
        else:
            logging.warning(f"Bot not found at station ({self.x}, {self.y}).")

    def share_information(self) -> None:
        """
        Shares information among all bots at the station.
        """
        if len(self.bots) > 1:
            logging.info(f"Bots at station ({self.x}, {self.y}) are sharing information.")
            for bot in self.bots:
                for other_bot in self.bots:
                    if bot != other_bot:
                        bot.known_parts.update(other_bot.known_parts)
                        bot.known_stations.update(other_bot.known_stations)
                        bot.known_drones.update(other_bot.known_drones)
                        bot.known_swarms.update(other_bot.known_swarms)

    # -------------------------------------------------------------------------
    # Bot Replication
    # -------------------------------------------------------------------------
    def can_replicate(self) -> bool:
        """
        Checks if the station has enough resources to replicate a bot.

        Returns:
            bool: True if replication is possible, False otherwise.
        """
        return len(self.stored_parts) >= 3

    def replicate_bot(self) -> Optional[SurvivorBot]:
        """
        Replicates a bot if conditions are met.

        Returns:
            Optional[SurvivorBot]: The new bot if replication occurs, otherwise None.
        """
        if self.can_replicate():
            repair_bots = [b for b in self.bots if b.bot_type == BotType.REPAIR]
            gatherer_bots = [b for b in self.bots if b.bot_type == BotType.GATHERER]

            if repair_bots and gatherer_bots:
                roll = random.random()
                if roll < 0.2:
                    new_bot = SurvivorBot(self.x, self.y, BotType.GATHERER)
                    logging.info(f"New gatherer bot replicated at station ({self.x}, {self.y}).")
                elif roll < 0.25:
                    new_bot = SurvivorBot(self.x, self.y, BotType.REPAIR)
                    logging.info(f"New repair bot replicated at station ({self.x}, {self.y}).")
                else:
                    logging.info(f"Replication failed (roll={roll:.2f}).")
                    return None

                # Deduct three parts
                for _ in range(3):
                    self.stored_parts.pop(0)

                return new_bot

        logging.warning(f"Not enough resources to replicate a bot at station ({self.x}, {self.y}).")
        return None
