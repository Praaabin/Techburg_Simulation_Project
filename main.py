from controller.simulation_controller import SimulationController
import argparse
import logging

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the Techburg Simulation.")
    parser.add_argument("--grid-size", type=int, default=30, help="The size of the simulation grid (default: 30).")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize the simulation controller
    try:
        controller = SimulationController(grid_size=args.grid_size)
        controller.setup()
        controller.run_simulation()
    except Exception as e:
        logging.critical(f"Simulation failed with error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()