import logging
from typing import Optional, List, Tuple

# Set up logging for professional debugging and tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Grid:
    def __init__(self, width: int, height: int):
        """
        Initialize the grid with the given dimensions.

        Args:
            width (int): The width of the grid.
            height (int): The height of the grid.
        """
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        logging.info(f"Grid initialized with dimensions {self.width}x{self.height}.")

    def wrap_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Wrap coordinates to simulate a toroidal (wrapping) grid.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.

        Returns:
            Tuple[int, int]: The wrapped coordinates.
        """
        return x % self.width, y % self.height

    def add_entity(self, x: int, y: int, entity) -> None:
        """
        Add an entity to the grid at the specified coordinates.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            entity: The entity to add (e.g., bot, drone, swarm, part, station).
        """
        x, y = self.wrap_coordinates(x, y)
        if self.grid[y][x] is not None:
            logging.warning(f"Entity already exists at ({x}, {y}). Overwriting.")
        self.grid[y][x] = entity
        logging.info(f"Entity added at ({x}, {y}).")

    def remove_entity(self, x: int, y: int) -> None:
        """
        Remove an entity from the grid at the specified coordinates.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
        """
        x, y = self.wrap_coordinates(x, y)
        if self.grid[y][x] is None:
            logging.warning(f"No entity found at ({x}, {y}).")
        else:
            self.grid[y][x] = None
            logging.info(f"Entity removed from ({x}, {y}).")

    def get_entity(self, x: int, y: int):
        """
        Get the entity at the specified coordinates.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.

        Returns:
            The entity at the specified coordinates, or None if no entity exists.
        """
        x, y = self.wrap_coordinates(x, y)
        return self.grid[y][x]

    def get_all_entities(self) -> List[Tuple[int, int, object]]:
        """
        Get a list of all entities in the grid along with their coordinates.

        Returns:
            List[Tuple[int, int, object]]: A list of tuples containing (x, y, entity).
        """
        entities = []
        for y in range(self.height):
            for x in range(self.width):
                entity = self.grid[y][x]
                if entity is not None:
                    entities.append((x, y, entity))
        return entities

    def get_all_entities_of_type(self, entity_type) -> List[Tuple[int, int, object]]:
        """
        Get a list of all entities of a specific type in the grid along with their coordinates.

        Args:
            entity_type: The type of entity to filter by.

        Returns:
            List[Tuple[int, int, object]]: A list of tuples containing (x, y, entity).
        """
        entities = []
        for y in range(self.height):
            for x in range(self.width):
                entity = self.grid[y][x]
                if isinstance(entity, entity_type):
                    entities.append((x, y, entity))
        return entities

    def display(self) -> None:
        """
        Print the grid to the console for visualization.
        """
        for row in self.grid:
            print(" ".join(cell.symbol if cell else "." for cell in row))
        logging.info("Grid displayed.")

    def is_within_bounds(self, x: int, y: int) -> bool:
        """
        Check if the given coordinates are within the grid bounds.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.

        Returns:
            bool: True if the coordinates are within bounds, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def clear(self) -> None:
        """
        Clear the grid by removing all entities.
        """
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        logging.info("Grid cleared.")