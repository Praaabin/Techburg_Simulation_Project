import random
import math
import logging
from typing import List, Tuple, Optional

from model.grid import Grid
from model.survivor_bot import SurvivorBot, BotType
from model.spare_part import SparePart
from model.recharge_station import RechargeStation
from model.malfunctioning_drone import MalfunctioningDrone
from model.scavenger_swarm import ScavengerSwarm
from view.gui_view import GUIView

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SimulationController:


    def __init__(self, grid_size: int = 30, critical_energy_threshold: int = 5):
        self.grid_size = grid_size
        self.grid = Grid(self.grid_size, self.grid_size)
        self.critical_energy_threshold = critical_energy_threshold
        self.view = GUIView(self.grid, self)
        self.is_running = False
        self.simulation_step = 0

        # Track all entities
        self.bots: List[SurvivorBot] = []
        self.drones: List[MalfunctioningDrone] = []
        self.swarms: List[ScavengerSwarm] = []
        self.stations: List[RechargeStation] = []
        self.parts: List[SparePart] = []

        # Metrics
        self.bots_remaining = 0
        self.parts_collected = 0

    def setup(self):
        """
        Initialize or reset the simulation state.
        """
        self.grid.clear()
        self.bots = []
        self.drones = []
        self.swarms = []
        self.parts = []
        self.stations = []
        self.simulation_step = 0

        # Reset metrics
        self.bots_remaining = 0
        self.parts_collected = 0

        # 1) Add recharge stations
        station_positions = self._generate_scattered_positions(4)
        for x, y in station_positions:
            station = RechargeStation(x, y, capacity=5)
            self.stations.append(station)
            self.grid.add_entity(x, y, station)

        # 2) Add survivor bots
        bot_positions = self._generate_scattered_positions(6)
        for i, (x, y) in enumerate(bot_positions):
            bot_type = BotType.REPAIR if i < 3 else BotType.GATHERER
            bot = SurvivorBot(x, y, bot_type, energy=100)
            self.bots.append(bot)
            self.grid.add_entity(x, y, bot)

        # Update the bots_remaining metric
        self.bots_remaining = len(self.bots)

        # 3) Add spare parts
        part_positions = self._generate_scattered_positions(15)
        for x, y in part_positions:
            part_type = random.choice(["small", "medium", "large"])
            part = SparePart(x, y, part_type)
            self.parts.append(part)
            self.grid.add_entity(x, y, part)

    def _generate_scattered_positions(self, count: int) -> List[Tuple[int, int]]:
        """
        Generate scattered positions with a minimum distance apart.
        """
        positions = []
        min_distance = math.sqrt(self.grid_size * self.grid_size / (count * 2))

        while len(positions) < count:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if self.grid.get_entity(x, y) is None and all(
                math.sqrt((x - px) ** 2 + (y - py) ** 2) >= min_distance
                for px, py in positions
            ):
                positions.append((x, y))
        return positions

    def update_simulation(self):
        """
        Main simulation loop.
        """
        if self.is_running:
            self.simulation_step += 1
            logging.info(f"Simulation Step: {self.simulation_step}")

            # Dynamically add drones and swarms
            if self.simulation_step % 10 == 0 and len(self.drones) < 4:
                self._add_drone()
            if self.simulation_step % 15 == 0 and len(self.swarms) < 3:
                self._add_swarm()

            # Update spare parts
            for part in self.parts[:]:
                if part.is_in_station:
                    part.recharge()
                else:
                    part.update_corrosion()
                if part.is_corroded():
                    self._remove_part(part, "corroded")

            # Update survivor bots
            for bot in self.bots[:]:
                if bot.is_active:
                    self._update_bot(bot)
                else:
                    bot.handle_inactive_removal(self.grid)
                    if not bot.is_active:
                        self.bots.remove(bot)

            # Update drones
            for drone in self.drones:
                self._update_drone(drone)

            # Update swarms
            for swarm in self.swarms[:]:
                swarm.update(self.grid, self.bots, self.drones, self.swarms)

            # Update the bots_remaining metric
            self.bots_remaining = len(self.bots)

            # Update the parts_collected metric
            self.parts_collected = sum(
                station.capacity - len(station.stored_parts) for station in self.stations
            )

            # Check end conditions
            if self._check_end_conditions():
                self.is_running = False
                logging.info("Simulation ended!")
                self.view.status_label.config(text="Simulation Status: Ended")
                self.view.log_message("Simulation ended.")
                return

            # Render the updated state
            self.view.render_grid()

            # Schedule the next step
            delay_ms = int(1000 / self.view.current_speed_factor)
            self.view.window.after(delay_ms, self.update_simulation)

    def _add_drone(self):
        """
        Add a malfunctioning drone to the grid.
        """
        x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
        if self.grid.get_entity(x, y) is None:
            drone = MalfunctioningDrone(x, y)
            self.drones.append(drone)
            self.grid.add_entity(x, y, drone)
            logging.info(f"Drone added at ({x}, {y}).")

    def _add_swarm(self):
        """
        Add a scavenger swarm to the grid.
        """
        x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
        if self.grid.get_entity(x, y) is None:
            swarm = ScavengerSwarm(x, y)
            self.swarms.append(swarm)
            self.grid.add_entity(x, y, swarm)
            logging.info(f"Swarm added at ({x}, {y}).")

    def reset_simulation(self):
        self.is_running = False
        self.setup()
        self.view.status_label.config(text="Simulation Status: Reset")
        self.view.log_message("Simulation reset.")
        self.view.render_grid()

    def _remove_part(self, part: SparePart, reason: str):
        """
        Remove a part from the grid and internal list.
        """
        self.grid.remove_entity(part.x, part.y)
        if part in self.parts:
            self.parts.remove(part)
        logging.info(f"Part removed at ({part.x}, {part.y}). Reason: {reason}")

    def _update_bot(self, bot: SurvivorBot):
        """
        Update a bot's behavior based on its energy, surroundings, and collaboration.
        """
        if not bot.is_active:
            # Attempt to reactivate the bot using nearby bots.
            for other_bot in self.bots:
                if other_bot != bot and self._distance(bot, other_bot) <= 1:
                    other_bot.transfer_energy(bot)
            bot.handle_inactive_removal(self.grid)
            return

        # Handle critically low energy: move to nearest station or consume parts.
        if bot.energy <= self.critical_energy_threshold:
            nearest_station = self._find_nearest_station(bot)
            if nearest_station:
                bot.move_toward(nearest_station.x, nearest_station.y, self.grid, self.simulation_step)
            bot.rest_or_consume_parts(self.grid)
            return

        # Handle part transportation: deposit part at the nearest recharge station.
        if bot.has_part:
            self._move_bot_to_station(bot, deposit=True)
            return

        # Threat avoidance: move away from nearby threats.
        nearest_threat = self._find_nearest_threat(bot)
        if nearest_threat and self._distance(bot, nearest_threat) <= bot.threat_detection_range:
            self._move_away_from_threat(bot, nearest_threat)
            return

        # Search for and collect parts if not carrying one.
        nearest_part = self._find_nearest_part(bot)
        if nearest_part:
            bot.move_toward(nearest_part.x, nearest_part.y, self.grid, self.simulation_step)
            bot.detect_and_collect_part(self.grid)
            return

        # If the bot is at a recharge station, handle various actions.
        current_station = self.grid.get_entity(bot.x, bot.y)
        if isinstance(current_station, RechargeStation):
            bot.rest_or_consume_parts(self.grid)

            # Share information with other bots at the same station.
            for other_bot in self.bots:
                if other_bot != bot and bot.x == other_bot.x and bot.y == other_bot.y:
                    bot.share_information(other_bot)

            # Attempt replication if another bot is at the station.
            for other_bot in self.bots:
                if other_bot != bot and bot.x == other_bot.x and bot.y == other_bot.y:
                    new_bot = bot.replicate_bot(other_bot, self.grid)
                    if new_bot:
                        self.bots.append(new_bot)

        # Default behavior: rest to regain energy or upgrade abilities.
        bot.rest_or_consume_parts(self.grid)


    def _move_bot_to_station(self, bot: SurvivorBot, deposit=False):
        """
        Move the bot to the nearest station and handle recharging or part deposit.
        """
        station = self._find_nearest_station(bot)
        if station:
            bot.move_toward(station.x, station.y, self.grid, self.simulation_step)
            if (bot.x, bot.y) == (station.x, station.y):
                if deposit and bot.has_part:
                    station.store_part(bot.carried_part)
                    bot.carried_part = None
                    bot.has_part = False

    def _find_nearest_part(self, bot: SurvivorBot) -> Optional[SparePart]:
        """
        Find the nearest spare part for the bot.
        """
        nearest_part = None
        min_dist = float('inf')
        for part in self.parts:
            dist = abs(bot.x - part.x) + abs(bot.y - part.y)
            if dist < min_dist:
                min_dist = dist
                nearest_part = part
        return nearest_part

    def _find_nearest_station(self, bot: SurvivorBot) -> Optional[RechargeStation]:
        """
        Find the nearest recharge station for the bot.
        """
        nearest_station = None
        min_dist = float('inf')
        for station in self.stations:
            dist = abs(bot.x - station.x) + abs(bot.y - station.y)
            if dist < min_dist:
                min_dist = dist
                nearest_station = station
        return nearest_station

    def _find_nearest_threat(self, bot: SurvivorBot) -> Optional[Tuple[int, int]]:
        """
        Find the nearest drone or swarm.
        """
        threats = self.drones + self.swarms
        nearest_threat = None
        min_dist = float('inf')
        for threat in threats:
            dist = abs(bot.x - threat.x) + abs(bot.y - threat.y)
            if dist < min_dist:
                min_dist = dist
                nearest_threat = threat
        return nearest_threat

    def _move_away_from_threat(self, bot: SurvivorBot, threat):
        """
        Move the bot away from a nearby threat.
        """
        dx = bot.x - threat.x
        dy = bot.y - threat.y

        if abs(dx) > abs(dy):
            new_x = bot.x + (1 if dx > 0 else -1)
            new_y = bot.y
        else:
            new_x = bot.x
            new_y = bot.y + (1 if dy > 0 else -1)

        if self.grid.is_within_bounds(new_x, new_y) and self.grid.get_entity(new_x, new_y) is None:
            bot.move_to(new_x, new_y, self.grid)

    def _distance(self, entity1, entity2) -> int:
        return abs(entity1.x - entity2.x) + abs(entity1.y - entity2.y)

    def _update_drone(self, drone: MalfunctioningDrone):
        """
        Update drone behavior: pursuit and attack.
        """
        if drone.energy <= 20:
            drone.recharge()
        else:
            nearest_bot = self._find_nearest_bot(drone)
            if nearest_bot:
                drone.move_toward(nearest_bot.x, nearest_bot.y, self.grid)
                if (drone.x, drone.y) == (nearest_bot.x, nearest_bot.y):
                    drone.attack(nearest_bot)

    def _find_nearest_bot(self, drone: MalfunctioningDrone) -> Optional[SurvivorBot]:
        """
        Find the nearest bot for the drone to attack.
        """
        nearest_bot = None
        min_dist = float('inf')
        for bot in self.bots:
            dist = abs(drone.x - bot.x) + abs(drone.y - bot.y)
            if dist < min_dist:
                min_dist = dist
                nearest_bot = bot
        return nearest_bot

    def _check_end_conditions(self) -> bool:
        """
        Check if the simulation should end.
        """
        return not self.parts or not self.bots

    def toggle_simulation(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.view.start_pause_button.config(text="Pause")
            self.view.status_label.config(text="Simulation Status: Running")
            self.update_simulation()
        else:
            self.view.start_pause_button.config(text="Resume")
            self.view.status_label.config(text="Simulation Status: Paused")

    def run_simulation(self):
        self.setup()
        self.update_simulation()
        self.view.run()

    def _handle_collaboration_and_replication(self):
        """
        Handle bot collaboration and replication at recharge stations.
        """
        for station in self.stations:
            bots_at_station = [bot for bot in self.bots if (bot.x, bot.y) == (station.x, station.y)]

            # Share information among bots
            for i in range(len(bots_at_station)):
                for j in range(i + 1, len(bots_at_station)):
                    bots_at_station[i].share_information(bots_at_station[j])

            # Replicate new bots if conditions are met
            for bot1 in bots_at_station:
                for bot2 in bots_at_station:
                    if bot1 != bot2 and bot1.bot_type != bot2.bot_type:
                        new_bot = bot1.replicate_bot(bot2, self.grid)
                        if new_bot:
                            self.bots.append(new_bot)
                            self.grid.add_entity(new_bot.x, new_bot.y, new_bot)

    def _assist_inactive_bots(self):
        """
        Allow fully charged bots to assist inactive bots by transferring energy.
        """
        for bot in self.bots:
            if bot.is_active and bot.energy >= 20:
                for inactive_bot in self.bots:
                    if not inactive_bot.is_active and self._distance(bot, inactive_bot) == 1:
                        bot.transfer_energy(inactive_bot)
