"""
The main application orchestrator.
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import random
import numpy as np
import heapq
import matplotlib.pyplot as plt
from collections import Counter
import csv
import os
import copy

from .main_window import MainWindow
from .dialogs.tree_dialogs import AddTreeDialog, DeleteTreeDialog, ModifyHealthDialog
from .dialogs.path_dialogs import ShortestPathDialog
from .dialogs.data_dialog import LoadDataDialog
from .handlers.canvas_events import CanvasEventsHandler
from .handlers.ui_actions import UIActions

from forest_management_system.components.forest_graph import ForestGraph
from forest_management_system.components.tree import Tree
from forest_management_system.components.path import Path
from forest_management_system.components.health_status import HealthStatus
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.pathfinding import find_shortest_path
from forest_management_system.algorithms.reserve_detection import find_reserves

class AppLogic:
    def __init__(self, root):
        self.root = root
        self.forest_graph = ForestGraph()
        self.tree_positions = {}
        self._pre_infection_health = {}
        
        # Snapshot storage for original imported data
        self.has_snapshot = False
        self.snapshot_forest_graph = None
        self.snapshot_tree_positions = None

        self.main_window = MainWindow(root)
        
        # Handlers
        self.ui_actions = UIActions(self)
        self.canvas_handler = CanvasEventsHandler(self)

        # Connections
        self.main_window.control_panel.connect_actions(self.ui_actions)
        self.main_window.forest_canvas.setup_canvas_bindings(self.canvas_handler)
        
        self.status_bar = self.main_window.status_bar
        self.update_display()

    def update_display(self):
        """Redraws the canvas and updates the info panel."""
        self.main_window.forest_canvas.draw_forest(self.forest_graph, self.tree_positions)
        self.main_window.info_panel.update_info(self.forest_graph, find_reserves)
        
    def create_snapshot(self):
        """Create a snapshot of the current forest data."""
        self.snapshot_forest_graph = copy.deepcopy(self.forest_graph)
        self.snapshot_tree_positions = copy.deepcopy(self.tree_positions)
        self.has_snapshot = True
        
    def restore_snapshot(self):
        """Restore the forest data from the snapshot."""
        if self.has_snapshot:
            self.forest_graph = copy.deepcopy(self.snapshot_forest_graph)
            self.tree_positions = copy.deepcopy(self.snapshot_tree_positions)
            self.update_display()
            return True
        return False

    def run(self):
        """Starts the Tkinter main loop."""
        self.root.mainloop() 