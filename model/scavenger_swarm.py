import logging
from typing import List, Tuple, Optional
from model.grid import Grid
from model.survivor_bot import SurvivorBot
from model.spare_part import SparePart
from model.malfunctioning_drone import MalfunctioningDrone

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ScavengerSwarm:
    """
    Represents a scavenger swarm in the post-apocalyptic city of Techburg.
    Swarms roam the grid, dismantling inactive bots and parts, emitting a decay field,
    merging with other swarms, and self-replicating when they gather enough material.
    """

    def __init__(self, x: int, y: int, size: int = 1, energy: float = 100.0):
        """
        Initializes a ScavengerSwarm instance.

        Args:
            x (int): The x-coordinate of the swarm's position.
            y (int): The y-coordinate of the swarm's position.
            size (int, optional): The initial size of the swarm. Defaults to 1.
            energy (float, optional): The initial energy level of the swarm. Defaults to 100.0.
        """
        self.x = x
        self.y = y
        self.size = size
        self.energy = energy
        self.symbol = 'W'  # Representation on the grid (optional for ASCII)
        self.material_collected = 0  # Tracks material gathered for replication

        logging.info(f"Scavenger swarm created at ({self.x}, {self.y}).")

    # -------------------------------------------------------------------------
    # Consuming a part
    # -------------------------------------------------------------------------
    def collect_part(self, part: SparePart, grid: Grid) -> None:
        """
        Collect and consume a spare part to boost the swarm's energy.

        Args:
            part (SparePart): The spare part to consume.
            grid (Grid): The grid on which the swarm is operating.
        """
        if part.is_consumed:
            logging.warning(f"Part at ({part.x}, {part.y}) already consumed.")
            return

        # The swarm calls part.consume_by_swarm() which sets part.is_consumed = True
        energy_boost = part.consume_by_swarm()
        self.energy += energy_boost  # e.g., +1%, +2%, +3% depending on small/med/large
        self.material_collected += 10  # Example: Increase material collected by 10

        # Remove from the grid entirely
        grid.remove_entity(part.x, part.y)
        logging.info(
            f"Swarm at ({self.x}, {self.y}) consumed part at ({part.x}, {part.y}). "
            f"Energy boost: {energy_boost}% (new energy={self.energy}%)."
        )

    # -------------------------------------------------------------------------
    # Decay field
    # -------------------------------------------------------------------------
    def emit_decay_field(self, entities: List) -> None:
        """
        Emits a decay field that reduces the energy of nearby bots and drones by 3% per step.

        Args:
            entities (List): A list of entities (bots and drones) within one cell of the swarm.
        """
        for entity in entities:
            if isinstance(entity, (SurvivorBot, MalfunctioningDrone)):
                old_energy = entity.energy
                # Reduce by 3% of current energy => multiply by 0.97
                entity.energy = max(0, entity.energy * 0.97)
                logging.info(
                    f"Swarm at ({self.x},{self.y}) decay field: {entity.__class__.__name__} at "
                    f"({entity.x},{entity.y}) {old_energy}% -> {entity.energy:.1f}%."
                )

    # -------------------------------------------------------------------------
    # Dismantle inactive bots or corroded parts in swarm cell
    # -------------------------------------------------------------------------
    def dismantle_inactive_entities(self, grid: Grid) -> None:
        """
        Dismantles inactive bots (energy=0) or corroded parts in the swarm's cell,
        collecting more material.
        """
        entity = grid.get_entity(self.x, self.y)
        if isinstance(entity, SurvivorBot) and entity.energy <= 0:
            # Dismantle the bot => remove from grid, gain material
            grid.remove_entity(self.x, self.y)
            self.material_collected += 10
            logging.info(f"Swarm at ({self.x},{self.y}) dismantled an inactive bot.")
        elif isinstance(entity, SparePart):
            # We only dismantle it if fully corroded => is_corroded()
            if entity.is_corroded():
                grid.remove_entity(self.x, self.y)
                self.material_collected += 5
                logging.info(f"Swarm at ({self.x},{self.y}) dismantled a corroded part.")

    # -------------------------------------------------------------------------
    # Merge with another swarm
    # -------------------------------------------------------------------------
    def merge(self, other_swarm: 'ScavengerSwarm') -> None:
        """
        Merges with another swarm to form a larger swarm.

        Args:
            other_swarm (ScavengerSwarm): The swarm to merge with.
        """
        self.size += other_swarm.size
        self.energy += other_swarm.energy
        self.material_collected += other_swarm.material_collected
        logging.info(
            f"Swarm at ({self.x},{self.y}) merged with swarm at "
            f"({other_swarm.x},{other_swarm.y}). New size={self.size}, energy={self.energy}%."
        )

    # -------------------------------------------------------------------------
    # Replicate if enough material
    # -------------------------------------------------------------------------
    def replicate(self) -> Optional['ScavengerSwarm']:
        """
        If the swarm has enough material_collected (>=50), replicate => create new swarm.
        Returns the new swarm if replication occurs, else None.
        """
        if self.material_collected >= 50:
            self.material_collected = 0
            new_swarm = ScavengerSwarm(self.x, self.y, size=1)
            logging.info(f"Swarm at ({self.x},{self.y}) replicated; new swarm also at ({self.x},{self.y}).")
            return new_swarm
        return None

    # -------------------------------------------------------------------------
    # Movement logic
    # -------------------------------------------------------------------------
    def move_toward(self, target_x: int, target_y: int, grid: Grid) -> None:
        """
        Moves the swarm one step toward (target_x, target_y).
        No diagonal movement.
        """
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

        # Check or wrap grid bounds
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            grid.remove_entity(self.x, self.y)
            grid.add_entity(new_x, new_y, self)
            self.x = new_x
            self.y = new_y
            logging.info(f"Swarm moved to ({self.x},{self.y}).")
        else:
            logging.warning(f"Swarm at ({self.x},{self.y}) tried to move outside grid.")

    # -------------------------------------------------------------------------
    # Main update logic each step
    # -------------------------------------------------------------------------
    def update(
        self,
        grid: Grid,
        bots: List[SurvivorBot],
        drones: List[MalfunctioningDrone],
        swarms: List['ScavengerSwarm']
    ) -> None:
        """
        Called each simulation step from the controller. The swarm:
         - emits decay field to bots/drones within 1 cell
         - dismantles inactive bots/corroded parts in its own cell
         - merges with close swarms (<=1 cell)
         - replicates if enough material
         - moves toward nearest inactive bot or corroded part if found
        """
        # 1) Emit decay field
        # If your Grid does not have get_entities_in_range, you can do a manual check:
        nearby_entities = []
        for ny in range(self.y - 1, self.y + 2):
            for nx in range(self.x - 1, self.x + 2):
                if grid.is_within_bounds(nx, ny):
                    entity = grid.get_entity(nx, ny)
                    if entity and (nx, ny) != (self.x, self.y):
                        nearby_entities.append(entity)

        self.emit_decay_field(nearby_entities)

        # 2) Dismantle inactive entities in current cell
        self.dismantle_inactive_entities(grid)

        # 3) Merge with close swarms
        for swarm in swarms[:]:
            if swarm != self:
                dist = abs(self.x - swarm.x) + abs(self.y - swarm.y)
                if dist <= 1:
                    self.merge(swarm)
                    swarms.remove(swarm)

        # 4) Replicate if enough material
        new_swarm = self.replicate()
        if new_swarm:
            swarms.append(new_swarm)
            # Also place the new swarm on the grid
            grid.add_entity(new_swarm.x, new_swarm.y, new_swarm)

        # 5) Move toward nearest inactive bot or corroded part
        target = self._find_nearest_target(grid, bots)
        if target:
            self.move_toward(target[0], target[1], grid)

    # -------------------------------------------------------------------------
    # Internal method: find nearest inactive bot or corroded part
    # -------------------------------------------------------------------------
    def _find_nearest_target(self, grid: Grid, bots: List[SurvivorBot]) -> Optional[Tuple[int, int]]:
        """
        Finds the nearest inactive bot (energy=0) or corroded part for the swarm to move towards.

        Returns (x, y) or None if no target found.
        """
        nearest_target = None
        min_distance = float('inf')

        # Check all bots for inactivity
        for bot in bots:
            if bot.energy <= 0:  # inactive
                dist = abs(self.x - bot.x) + abs(self.y - bot.y)
                if dist < min_distance:
                    min_distance = dist
                    nearest_target = (bot.x, bot.y)

        # Check all corroded parts
        for y in range(grid.height):
            for x in range(grid.width):
                entity = grid.get_entity(x, y)
                if isinstance(entity, SparePart) and entity.is_corroded():
                    dist = abs(self.x - x) + abs(self.y - y)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_target = (x, y)

        return nearest_target
