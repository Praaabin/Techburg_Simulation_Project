import tkinter as tk
from tkinter import ttk
from typing import Dict
from model.grid import Grid
from model.survivor_bot import SurvivorBot
from model.spare_part import SparePart
from model.recharge_station import RechargeStation
from model.malfunctioning_drone import MalfunctioningDrone
from model.scavenger_swarm import ScavengerSwarm

class GUIView:
    """
    Represents the GUI view for the Techburg simulation. This class provides an advanced
    and professional visualization of the simulation, including dynamic entity rendering,
    interactive controls, status panels, and performance metrics.
    """

    def __init__(self, grid: Grid, controller, cell_size: int = 30):
        """
        Initializes the GUI view with a reference to the grid and sets up the Tkinter window.

        Args:
            grid (Grid): The grid representing the simulation world.
            controller: The controller managing the simulation (SimulationController).
            cell_size (int, optional): The size of each cell in pixels. Defaults to 30.
        """
        self.grid = grid
        self.controller = controller  # Reference to the SimulationController
        self.cell_size = cell_size

        # Track the current speed factor from the slider (1–10)
        self.current_speed_factor = 1.0

        # Initialize the Tkinter window
        self.window = tk.Tk()
        self.window.title("Techburg Simulation")
        self.window.geometry("1400x900")  # Larger window

        # Set up the canvas for grid rendering
        self.canvas = tk.Canvas(
            self.window,
            width=self.grid.width * self.cell_size,
            height=self.grid.height * self.cell_size,
            bg="white"
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Set up the status panel
        self.status_panel = ttk.Frame(self.window, width=400, padding="10")
        self.status_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Add simulation controls
        self.setup_controls()

        # Add a status display
        self.status_label = ttk.Label(self.status_panel, text="Simulation Status: Reset", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Add entity counters
        self.entity_counters = {}
        self.setup_entity_counters()

        # Add performance metrics display
        self.setup_performance_metrics()

        # Add a log display
        self.log_text = tk.Text(self.status_panel, height=10, width=50, state=tk.DISABLED)
        self.log_text.pack(pady=10)

        # Add a legend for entity symbols
        self.setup_legend()

        # Add a log display
        self.log_text = tk.Text(self.status_panel, height=10, width=50, state=tk.DISABLED)
        self.log_text.pack(pady=10)

    def setup_controls(self):
        """
        Sets up interactive controls for the simulation.
        """
        controls_frame = ttk.Frame(self.status_panel)
        controls_frame.pack(pady=10)

        # Start/Pause button
        self.start_pause_button = ttk.Button(controls_frame, text="Start", command=self.toggle_simulation)
        self.start_pause_button.pack(side=tk.LEFT, padx=5)

        # Reset button
        self.reset_button = ttk.Button(controls_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Speed control slider
        self.speed_label = ttk.Label(controls_frame, text="Speed: 1x")
        self.speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_slider = ttk.Scale(
            controls_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            command=self.update_speed
        )
        self.speed_slider.set(1)  # Default speed
        self.speed_slider.pack(side=tk.LEFT, padx=5)

    def update_speed(self, value: str):
        """
        Called when the user drags the speed slider (1–10).
        We'll interpret this as a speed factor: 1 => slow, 10 => fast.
        """
        self.current_speed_factor = float(value)
        self.speed_label.config(text=f"Speed: {value}x")
        self.controller.simulation_delay = int(1000 / self.current_speed_factor)
        self.log_message(f"Simulation speed updated to {value}x.")

    def setup_entity_counters(self):
        """
        Sets up counters for displaying the number of each entity type.
        """
        entity_types = ["Survivor Bots", "Drones", "Swarms", "Parts", "Stations"]
        for entity_type in entity_types:
            frame = ttk.Frame(self.status_panel)
            frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(frame, text=f"{entity_type}:", width=20, anchor=tk.W)
            label.pack(side=tk.LEFT)

            counter = ttk.Label(frame, text="0", width=10, anchor=tk.E)
            counter.pack(side=tk.RIGHT)

            self.entity_counters[entity_type] = counter

    def setup_performance_metrics(self):
        """
        Adds performance metrics to the GUI for tracking the simulation progress.
        """
        metrics_frame = ttk.LabelFrame(self.status_panel, text="Performance Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, pady=10)

        self.parts_collected_label = ttk.Label(metrics_frame, text="Parts Collected: 0", font=("Arial", 10))
        self.parts_collected_label.pack(anchor=tk.W)

        self.bots_remaining_label = ttk.Label(metrics_frame, text="Bots Remaining: 0", font=("Arial", 10))
        self.bots_remaining_label.pack(anchor=tk.W)

    def setup_legend(self):
        """
        Sets up a professional and visually appealing legend to display the symbols
        and their corresponding entity names.
        """
        legend_frame = ttk.LabelFrame(self.status_panel, text="Techburg Guide", padding="10")
        legend_frame.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X)

        legend_entries = [
            ("Survivor Bots", "blue", "circle"),
            ("Drones", "red", "triangle"),
            ("Swarms", "purple", "circle"),
            ("Spare Parts", "green", "square"),
            ("Stations", "orange", "square")
        ]

        for name, color, shape in legend_entries:
            frame = ttk.Frame(legend_frame)
            frame.pack(fill=tk.X, pady=2, padx=5)

            canvas = tk.Canvas(frame, width=20, height=20, bg="white", highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=(0, 10))

            if shape == "circle":
                canvas.create_oval(2, 2, 18, 18, fill=color, outline="black")
            elif shape == "square":
                canvas.create_rectangle(2, 2, 18, 18, fill=color, outline="black")
            elif shape == "triangle":
                canvas.create_polygon(10, 2, 2, 18, 18, 18, fill=color, outline="black")

            label = ttk.Label(frame, text=name, font=("Arial", 10))
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def render_grid(self):
        """
        Draws the grid and entities on the canvas with advanced visualization.
        """
        self.canvas.delete("all")

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

                entity = self.grid.get_entity(x, y)
                if entity:
                    self.draw_entity(entity, x1, y1, x2, y2)

        self.update_entity_counters()
        self.update_performance_metrics()

    def draw_entity(self, entity, x1: int, y1: int, x2: int, y2: int):
        """
        Draws an entity on the canvas based on its type.
        """
        if isinstance(entity, SurvivorBot):
            self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="blue", tags="bot")
            self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=f"{entity.energy:.0f}", fill="white", font=("Arial", 9, "bold"))
        elif isinstance(entity, SparePart):
            self.canvas.create_rectangle(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="green", tags="part")
        elif isinstance(entity, RechargeStation):
            self.canvas.create_rectangle(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill="orange", tags="station")
        elif isinstance(entity, MalfunctioningDrone):
            self.canvas.create_polygon(x1 + 5, y1 + 5, x2 - 5, y1 + 5, (x1 + x2) // 2, y2 - 5, fill="red", tags="drone")
        elif isinstance(entity, ScavengerSwarm):
            self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="purple", tags="swarm")

    def update_entity_counters(self):
        """
        Updates the entity counters in the status panel.
        """
        counts = {
            "Survivor Bots": len(self.grid.get_all_entities_of_type(SurvivorBot)),
            "Drones": len(self.grid.get_all_entities_of_type(MalfunctioningDrone)),
            "Swarms": len(self.grid.get_all_entities_of_type(ScavengerSwarm)),
            "Parts": len(self.grid.get_all_entities_of_type(SparePart)),
            "Stations": len(self.grid.get_all_entities_of_type(RechargeStation)),
        }

        for entity_type, count in counts.items():
            self.entity_counters[entity_type].config(text=str(count))

    def update_performance_metrics(self):
        """
        Updates the performance metrics display.
        """
        self.parts_collected_label.config(text=f"Parts Collected: {self.controller.parts_collected}")
        self.bots_remaining_label.config(text=f"Bots Remaining: {self.controller.bots_remaining}")

    def log_message(self, message: str):
        """
        Logs a message to the status panel.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def toggle_simulation(self):
        """
        Toggles the simulation between running and paused states.
        """
        if self.start_pause_button["text"] == "Pause":
            self.start_pause_button.config(text="Resume")
            self.status_label.config(text="Simulation Status: Paused")
            self.controller.is_running = False
        else:
            if self.start_pause_button["text"] == "Start":
                self.controller.reset_simulation()
                self.controller.is_running = True
            else:
                self.controller.is_running = True
            self.start_pause_button.config(text="Pause")
            self.status_label.config(text="Simulation Status: Running")
            self.controller.update_simulation()

    def reset_simulation(self):
        """
        Resets the simulation to its initial state.
        """
        self.controller.is_running = False
        self.controller.reset_simulation()
        self.start_pause_button.config(text="Start")
        self.status_label.config(text="Simulation Status: Reset")
        self.log_message("Simulation reset.")
        self.render_grid()

    def run(self):
        """
        Starts the Tkinter main event loop.
        """
        self.window.mainloop()