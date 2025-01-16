import logging
import random
from typing import Optional, List

from model.grid import Grid
from model.survivor_bot import SurvivorBot, BotType
from model.spare_part import SparePart

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MalfunctioningDrone:
    """
    Represents a malfunctioning drone in Techburg.
    - Detects survivor bots within 3 cells by default (Manhattan distance).
    - Pursues them, costing 20% energy each time it actually catches a bot.
    - Attacks the bot (shock or disable). If the bot is 'repair' type, the drone
      destroys it completely.
    - Causes the bot to drop any carried part (the bot logs that location).
    - If energy <= 20, the drone hibernates and recharges +10% each step until 100%.
    """

    def __init__(self, x: int, y: int,
                 energy: float = 100.0,
                 detection_range: int = 3):
        """
        Args:
            x (int): The drone's x-coordinate.
            y (int): The drone's y-coordinate.
            energy (float): Initial energy (0-100).
            detection_range (int): Range (in Manhattan distance) to detect bots. Default=3.
        """
        self.x = x
        self.y = y
        self.energy = energy
        self.detection_range = detection_range

        # If energy <= 20 => hibernating
        self.hibernating = False
        self.symbol = 'D'  # For console or ASCII representation

        logging.info(f"Malfunctioning drone created at ({self.x}, {self.y}), energy={self.energy}%.")

    def update(self, grid: Grid, bots: List[SurvivorBot]) -> None:
        """
        Called each simulation step from the controller.
        Handles detection, pursuit, hibernation, recharging, and attacking.
        """
        # If hibernating or energy <= 20 => recharge
        if self.hibernating or self.energy <= 20:
            self.recharge()
            return

        # Otherwise, detect nearest bot
        nearest_bot = self.detect_bots(bots)
        if nearest_bot:
            # Move closer
            self.move_toward(nearest_bot.x, nearest_bot.y, grid)

            # If on same tile => attack
            if (self.x, self.y) == (nearest_bot.x, nearest_bot.y):
                self.attack(nearest_bot)

                # Deplete 20% energy after a successful chase
                old_energy = self.energy
                self.energy = max(0, self.energy - 20)
                logging.info(
                    f"Drone at ({self.x}, {self.y}) pursuit cost 20% energy "
                    f"({old_energy}% -> {self.energy}%)."
                )

                # Possibly enter hibernation if now <= 20%
                if self.energy <= 20:
                    self.recharge()

    def detect_bots(self, bots: List[SurvivorBot]) -> Optional[SurvivorBot]:
        """
        Finds the nearest survivor bot within self.detection_range (Manhattan distance).
        Returns the nearest in range, or None if none in range.
        """
        nearest_bot = None
        min_distance = float('inf')

        for bot in bots:
            distance = abs(self.x - bot.x) + abs(self.y - bot.y)
            # Only detect if distance <= detection_range
            if distance <= self.detection_range and distance < min_distance:
                min_distance = distance
                nearest_bot = bot
        return nearest_bot

    def move_toward(self, target_x: int, target_y: int, grid: Grid) -> None:
        """
        Moves drone one step toward (target_x, target_y), if not hibernating.
        No diagonal movement.
        """
        if self.hibernating:
            logging.info(f"Drone at ({self.x}, {self.y}) is hibernating; cannot move.")
            return

        dx = 0
        dy = 0
        # Decide horizontal direction
        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1
        # Decide vertical direction
        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1

        new_x = self.x + dx
        new_y = self.y + dy

        # Check grid bounds or wrap-around if your grid is toroidal
        # (If your Grid does wrap automatically, or you call grid.wrap_coordinates, etc.)
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            # remove from old position
            grid.remove_entity(self.x, self.y)
            self.x = new_x
            self.y = new_y
            # add to new
            grid.add_entity(self.x, self.y, self)
            logging.info(f"Drone moved to ({self.x}, {self.y}).")

    def attack(self, bot: SurvivorBot) -> None:
        """
        Drone attacks a survivor bot:
         - If it's a repair bot => destroyed outright (bot.energy=0).
         - Otherwise, 50% chance to shock (bot -5%), or disable (bot -20%).
         - Force the bot to drop any carried part. The bot remembers that location.
        """
        if self.hibernating:
            logging.info(f"Drone at ({self.x}, {self.y}) is hibernating; cannot attack.")
            return

        if bot.bot_type == BotType.REPAIR:
            # Destroy repair bot outright
            bot.energy = 0
            logging.info(f"Drone destroyed repair bot at ({bot.x}, {bot.y}).")
        else:
            # 50% shock or disable
            if random.random() < 0.5:
                old_energy = bot.energy
                bot.energy = max(0, bot.energy - 5)
                logging.info(
                    f"Drone shocked bot at ({bot.x}, {bot.y}): "
                    f"{old_energy}% -> {bot.energy}%."
                )
            else:
                old_energy = bot.energy
                bot.energy = max(0, bot.energy - 20)
                logging.info(
                    f"Drone disabled bot at ({bot.x}, {bot.y}): "
                    f"{old_energy}% -> {bot.energy}%."
                )

        # Make the bot drop its part (bot logs location)
        if bot.has_part:
            dropped_location = (bot.x, bot.y)
            bot.drop_part(grid)  # bot.known_parts.add(dropped_location)
            logging.info(f"Bot at {dropped_location} dropped a part due to drone attack.")

    def recharge(self) -> None:
        """
        Drone hibernates at <= 20% energy, recharging by +10% each step
        until hitting 100%. Then it resumes normal operation.
        """
        if self.energy <= 20:
            self.hibernating = True
            logging.info(f"Drone at ({self.x}, {self.y}) is hibernating at {self.energy}%.")

        if self.hibernating:
            old_energy = self.energy
            self.energy = min(100.0, self.energy + 10.0)
            logging.info(f"Drone recharging: {old_energy}% -> {self.energy}% at ({self.x}, {self.y}).")

            if self.energy >= 100.0:
                self.hibernating = False
                logging.info(f"Drone at ({self.x}, {self.y}) fully recharged; resuming patrol.")
