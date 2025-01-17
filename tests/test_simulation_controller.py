import pytest
from unittest.mock import Mock, patch
from model.grid import Grid
from model.survivor_bot import SurvivorBot, BotType
from model.spare_part import SparePart
from model.recharge_station import RechargeStation
from model.malfunctioning_drone import MalfunctioningDrone
from model.scavenger_swarm import ScavengerSwarm
from controller.simulation_controller import SimulationController


# Mock tkinter to avoid TclError in headless environments
@pytest.fixture(autouse=True)
def mock_tkinter():
    with patch("tkinter.Tk"), patch("tkinter.Text"):
        yield


@pytest.fixture
def simulation_controller():
    """
    Fixture to create a SimulationController instance for testing.
    """
    return SimulationController(grid_size=30, critical_energy_threshold=5)


def test_initialization(simulation_controller):
    """
    Test the initialization of the SimulationController.
    """
    assert simulation_controller.grid_size == 30
    assert simulation_controller.critical_energy_threshold == 5
    assert simulation_controller.simulation_step == 0
    assert simulation_controller.is_running is False
    assert len(simulation_controller.bots) == 0
    assert len(simulation_controller.parts) == 0
    assert len(simulation_controller.stations) == 0


def test_setup(simulation_controller):
    """
    Test the setup method for initializing the simulation.
    """
    simulation_controller.setup()

    # Check the grid is populated
    assert len(simulation_controller.stations) == 4
    assert len(simulation_controller.bots) == 6
    assert len(simulation_controller.parts) == 15

    # Ensure entities are added to the grid
    for station in simulation_controller.stations:
        assert simulation_controller.grid.get_entity(station.x, station.y) == station

    for bot in simulation_controller.bots:
        assert simulation_controller.grid.get_entity(bot.x, bot.y) == bot

    for part in simulation_controller.parts:
        assert simulation_controller.grid.get_entity(part.x, part.y) == part


def test_add_drone(simulation_controller):
    """
    Test adding a malfunctioning drone to the grid.
    """
    simulation_controller.setup()
    simulation_controller._add_drone()
    assert len(simulation_controller.drones) == 1
    drone = simulation_controller.drones[0]
    assert isinstance(drone, MalfunctioningDrone)
    assert simulation_controller.grid.get_entity(drone.x, drone.y) == drone


def test_add_swarm(simulation_controller):
    """
    Test adding a scavenger swarm to the grid.
    """
    simulation_controller.setup()
    simulation_controller._add_swarm()
    assert len(simulation_controller.swarms) == 1
    swarm = simulation_controller.swarms[0]
    assert isinstance(swarm, ScavengerSwarm)
    assert simulation_controller.grid.get_entity(swarm.x, swarm.y) == swarm


def test_update_simulation(simulation_controller):
    """
    Test the update simulation process.
    """
    simulation_controller.setup()

    # Mock methods to avoid dependency on external classes
    simulation_controller._add_drone = Mock()
    simulation_controller._add_swarm = Mock()
    simulation_controller._update_bot = Mock()
    simulation_controller._update_drone = Mock()

    # Start the simulation
    simulation_controller.is_running = True
    simulation_controller.update_simulation()

    # Ensure simulation step increments
    assert simulation_controller.simulation_step == 1

    # Ensure bot update methods are called
    assert simulation_controller._update_bot.call_count == len(simulation_controller.bots)


def test_remove_part(simulation_controller):
    """
    Test the removal of corroded parts.
    """
    simulation_controller.setup()
    part = simulation_controller.parts[0]
    simulation_controller._remove_part(part, "corroded")

    # Check the part is removed from the grid and list
    assert part not in simulation_controller.parts
    assert simulation_controller.grid.get_entity(part.x, part.y) is None


def test_find_nearest_part(simulation_controller):
    """
    Test finding the nearest spare part for a bot.
    """
    simulation_controller.setup()
    bot = simulation_controller.bots[0]
    nearest_part = simulation_controller._find_nearest_part(bot)
    assert nearest_part in simulation_controller.parts


def test_find_nearest_station(simulation_controller):
    """
    Test finding the nearest recharge station for a bot.
    """
    simulation_controller.setup()
    bot = simulation_controller.bots[0]
    nearest_station = simulation_controller._find_nearest_station(bot)
    assert nearest_station in simulation_controller.stations


def test_move_away_from_threat(simulation_controller):
    """
    Test bot movement away from a threat.
    """
    simulation_controller.setup()
    bot = simulation_controller.bots[0]
    threat = Mock()
    threat.x, threat.y = bot.x - 1, bot.y

    # Simulate movement
    simulation_controller._move_away_from_threat(bot, threat)

    # Ensure the bot moved away
    assert bot.x > threat.x or bot.y != threat.y


def test_toggle_simulation(simulation_controller):
    """
    Test toggling the simulation status.
    """
    # Toggle the simulation on
    simulation_controller.toggle_simulation()
    assert simulation_controller.is_running is True

    # Toggle the simulation off
    simulation_controller.toggle_simulation()
    assert simulation_controller.is_running is False


def test_check_end_conditions(simulation_controller):
    """
    Test the end conditions for the simulation.
    """
    simulation_controller.setup()

    # No parts left
    simulation_controller.parts = []
    assert simulation_controller._check_end_conditions() is True

    # No bots left
    simulation_controller.bots = []
    assert simulation_controller._check_end_conditions() is True