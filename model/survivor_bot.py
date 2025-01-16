import random
import logging
from typing import List, Tuple, Optional, Set

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SparePart:
    """
    Placeholder SparePart class for demonstration.
    Assumes each part has a 'size' attribute: 'small', 'medium', or 'large'.
    """

    def __init__(self, size: str = "small"):
        self.size = size


class RechargeStation:
    """
    Placeholder RechargeStation class with basic logic for storing parts.
    """

    def __init__(self):
        self.stored_parts: List[SparePart] = []

    def store_part(self, part: SparePart):
        self.stored_parts.append(part)

    def remove_part(self, part: SparePart):
        if part in self.stored_parts:
            self.stored_parts.remove(part)

    def get_stored_parts(self) -> List[SparePart]:
        return self.stored_parts


class BotType:
    REPAIR = "repair"
    GATHERER = "gatherer"


# Constants for energy and enhancements
ENERGY_PER_MOVE = 5
CRITICAL_ENERGY_THRESHOLD = 5
INACTIVE_REMOVAL_STEPS = 5
PART_TOTAL_ENERGY = {"small": 10, "medium": 30, "large": 50}
PART_CONSUMPTION_RATE = {"small": 1, "medium": 3, "large": 5}
RESTING_RECHARGE_RATE = 1
MAX_SPEED_ENHANCEMENT = 100
MAX_VISION_ENHANCEMENT = 150


class SurvivorBot:
    def __init__(self, x: int, y: int, bot_type: str = BotType.GATHERER, energy: int = 100):
        self.x = x
        self.y = y
        self.bot_type = bot_type
        self.energy = energy
        self.energy_capacity = 100

        self.carried_part: Optional[SparePart] = None
        self.has_part = False
        self.is_active = True
        self.steps_inactive = 0

        self.speed_enhancement = 0
        self.vision_enhancement = 0
        self.consumption_in_progress = False
        self.consumption_accumulated = 0

        self.known_parts: Set[Tuple[int, int]] = set()
        self.known_stations: Set[Tuple[int, int]] = set()
        self.known_drones: Set[Tuple[int, int]] = set()
        self.known_swarms: Set[Tuple[int, int]] = set()

        # New attributes for threat avoidance
        self.threat_detection_range = 4
        self.escape_cooldown = 0
        self.last_threat_direction = None

        logging.info(f"SurvivorBot created at ({x}, {y}) as '{bot_type}' with {energy}% energy.")


    # -------------------------
    # Movement and Navigation
    # -------------------------
    def move_to(self, new_x: int, new_y: int, grid) -> bool:
        if not self.is_active:
            return False
        if grid.is_within_bounds(new_x, new_y) and grid.get_entity(new_x, new_y) is None:
            old_x, old_y = self.x, self.y
            grid.remove_entity(old_x, old_y)
            self.x, self.y = new_x, new_y
            grid.add_entity(self.x, self.y, self)
            self.energy -= ENERGY_PER_MOVE
            if self.energy <= 0:
                self.is_active = False
                logging.info(f"Bot at ({self.x}, {self.y}) became inactive due to low energy.")
            logging.info(f"Bot moved from ({old_x}, {old_y}) to ({new_x}, {new_y}).")
            return True
        return False

    def move_toward(self, target_x: int, target_y: int, grid, simulation_step: int) -> bool:
        if not self.is_active:
            return False
        can_move = self.speed_enhancement > 50 or simulation_step % 2 == 0
        if not can_move:
            return False
        old_x, old_y = self.x, self.y
        dx, dy = target_x - self.x, target_y - self.y
        if abs(dx) > abs(dy):
            step_x = 1 if dx > 0 else -1
            self.move_to(self.x + step_x, self.y, grid)
        else:
            step_y = 1 if dy > 0 else -1
            self.move_to(self.x, self.y + step_y, grid)
        return (self.x, self.y) != (old_x, old_y)

    # -------------------------
    # Detection and Collection
    # -------------------------
    def get_detection_range(self) -> int:
        if self.vision_enhancement <= 50:
            return 1
        elif self.vision_enhancement <= 100:
            return 2
        return 3

    def detect_and_collect_part(self, grid):
        if not self.is_active or self.has_part:
            return
        detection_range = self.get_detection_range()
        best_part, best_value, best_position = None, -1, None
        for dx in range(-detection_range, detection_range + 1):
            for dy in range(-detection_range, detection_range + 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = self.x + dx, self.y + dy
                if not grid.is_within_bounds(x, y):
                    continue
                entity = grid.get_entity(x, y)
                if isinstance(entity, SparePart):
                    value = PART_TOTAL_ENERGY.get(entity.size, 0)
                    if value > best_value:
                        best_part, best_value, best_position = entity, value, (x, y)
        if best_part and best_position:
            self.carried_part, self.has_part = best_part, True
            grid.remove_entity(*best_position)
            logging.info(f"Bot at ({self.x}, {self.y}) collected part at {best_position}.")
    # -------------------------
    # Transport and Deposit
    # -------------------------
    def deposit_part(self, grid):
        if not self.is_active or not self.has_part:
            return
        entity = grid.get_entity(self.x, self.y)
        if isinstance(entity, RechargeStation):
            entity.store_part(self.carried_part)
            self.carried_part, self.has_part = None, False
            logging.info(f"Bot at ({self.x}, {self.y}) deposited a part at the station.")
    # -------------------------
    # Energy Management
    # -------------------------
    def rest_or_consume_parts(self, grid):
        if not self.is_active:
            return
        entity = grid.get_entity(self.x, self.y)
        if not isinstance(entity, RechargeStation):
            return
        if self.energy <= CRITICAL_ENERGY_THRESHOLD and self.has_part:
            self.consume_part_immediately()
        elif self.has_part:
            self.consume_part_partially()
        elif self.energy < self.energy_capacity:
            self.energy = min(self.energy + RESTING_RECHARGE_RATE, self.energy_capacity)

    def consume_part_immediately(self):
        if self.has_part and self.carried_part:
            self.energy = min(self.energy + PART_TOTAL_ENERGY[self.carried_part.size], self.energy_capacity)
            self.carried_part, self.has_part = None, False

    def consume_part_partially(self):
        if self.has_part and self.carried_part:
            rate = PART_CONSUMPTION_RATE[self.carried_part.size]
            self.energy = min(self.energy + rate, self.energy_capacity)
            self.consumption_accumulated += rate
            if self.consumption_accumulated >= PART_TOTAL_ENERGY[self.carried_part.size]:
                self.carried_part, self.has_part = None, False

    def handle_inactive_removal(self, grid):
        if not self.is_active:
            self.steps_inactive += 1
            if self.steps_inactive >= INACTIVE_REMOVAL_STEPS:
                grid.remove_entity(self.x, self.y)


    # -------------------------
    # Upgrades and Enhancements
    # -------------------------
    def upgrade_ability(self, ability: str, amount: int):
        if ability == "speed":
            self.speed_enhancement = min(self.speed_enhancement + amount, MAX_SPEED_ENHANCEMENT)
        elif ability == "vision":
            self.vision_enhancement = min(self.vision_enhancement + amount, MAX_VISION_ENHANCEMENT)
        elif ability == "energy":
            self.energy_capacity += amount

    def share_information(self, other_bot):
        """
        Share knowledge with another bot about known parts, stations, and threats.
        """
        if not self.is_active or not other_bot.is_active:
            return

        self.known_parts.update(other_bot.known_parts)
        self.known_stations.update(other_bot.known_stations)
        self.known_drones.update(other_bot.known_drones)
        self.known_swarms.update(other_bot.known_swarms)
        logging.info(f"Bot at ({self.x}, {self.y}) shared information with bot at ({other_bot.x}, {other_bot.y}).")

    def transfer_energy(self, other_bot):
        """
        Transfer energy from this bot to another bot to reactivate it.
        Only applicable if the other bot is inactive and this bot has sufficient energy.
        """
        if self.energy > 20 and not other_bot.is_active:
            transfer_amount = min(20, self.energy - 20)
            self.energy -= transfer_amount
            other_bot.energy += transfer_amount
            if other_bot.energy > 0:
                other_bot.is_active = True
            logging.info(
                f"Bot at ({self.x}, {self.y}) transferred {transfer_amount}% energy to bot at ({other_bot.x}, {other_bot.y}).")

    def replicate_bot(self, other_bot, grid):
        """
        Attempt to replicate a new bot when two bots (repair and gatherer) are at the same recharge station.
        """
        if not self.is_active or not other_bot.is_active:
            return None

        station = grid.get_entity(self.x, self.y)
        if not isinstance(station, RechargeStation):
            return None

        # Probability-based replication logic
        if random.random() < 0.2:  # 20% chance for a gatherer bot
            if self.energy >= 30 and other_bot.energy >= 30:
                self.energy -= 30
                other_bot.energy -= 30
                new_bot = SurvivorBot(self.x, self.y, bot_type=BotType.GATHERER)
                logging.info(f"New gatherer bot replicated at ({self.x}, {self.y}).")
                return new_bot
        elif random.random() < 0.05:  # 5% chance for a repair bot
            if self.energy >= 50 and other_bot.energy >= 50:
                self.energy -= 50
                other_bot.energy -= 50
                new_bot = SurvivorBot(self.x, self.y, bot_type=BotType.REPAIR)
                logging.info(f"New repair bot replicated at ({self.x}, {self.y}).")
                return new_bot
        return None
