"""
Handles all actions triggered by the control panel buttons.
"""
import random
import numpy as np
import csv
import heapq
import matplotlib.pyplot as plt
from collections import Counter
from tkinter import messagebox, filedialog, simpledialog
import networkx as nx
from sklearn.manifold import MDS
import scipy.optimize
import tkinter as tk

from ...data_structures.tree import Tree
from ...data_structures.path import Path
from ...data_structures.health_status import HealthStatus
from ...io.dataset_loader import load_forest_from_files
from ...algorithms.pathfinding import find_shortest_path
from ..dialogs.tree_dialogs import AddTreeDialog, DeleteTreeDialog, ModifyHealthDialog
from ..dialogs.path_dialogs import ShortestPathDialog
from ..dialogs.data_dialog import LoadDataDialog
from forest_management_system.algorithms.force_layout import force_directed_layout

class UIActions:
    def __init__(self, app_logic):
        self.app = app_logic
        self.root = self.app.root
        self.canvas = self.app.main_window.forest_canvas
        self.control_panel = self.app.main_window.control_panel

        self.add_path_mode = False
        self.delete_path_mode = False
        self.infection_sim_mode = False

    # Tree Actions
    def add_tree(self):
        dialog = AddTreeDialog(self.root)
        result = dialog.show()
        if result:
            tree_id = max([t.tree_id for t in self.app.forest_graph.trees.values()], default=0) + 1
            tree = Tree(tree_id, result["species"], result["age"], result["health"])
            self.app.forest_graph.add_tree(tree)
            self.app.tree_positions[tree_id] = (random.uniform(10, 90), random.uniform(10, 90))
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Tree {tree_id} added.")

    def start_delete_tree(self):
        if not self.app.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees to delete.", parent=self.root)
            return
        self.delete_tree_mode = True
        self.app.status_bar.set_text("🖱️ Click a tree to delete...")
        self.control_panel.delete_tree_btn.config(text="✖ Exit", command=self.exit_delete_tree, style='Red.TButton')

    def exit_delete_tree(self):
        self.delete_tree_mode = False
        self.app.status_bar.set_text("Ready")
        self.control_panel.delete_tree_btn.config(text="✖ Delete Tree", command=self.start_delete_tree, style='Modern.TButton')
        self.app.update_display()

    def delete_tree_at_position(self, x, y):
        tree = self.app.canvas_handler._find_tree_at_position(x, y)
        if tree:
            self.app.forest_graph.remove_tree(tree.tree_id)
            if tree.tree_id in self.app.tree_positions:
                del self.app.tree_positions[tree.tree_id]
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Tree {tree.tree_id} deleted.")
        else:
            # Add message when no tree is found
            self.app.status_bar.set_text("No tree found at the selected position.")

    def modify_health(self):
        if not self.app.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees available.", parent=self.root)
            return
        
        tree_ids = list(self.app.forest_graph.trees.keys())
        dialog = ModifyHealthDialog(self.root, tree_ids)
        result = dialog.show()
        
        if result:
            tree_id = result["tree_id"]
            new_health = result["health"]
            self.app.forest_graph.update_health_status(tree_id, new_health)
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Tree {tree_id} health updated.")

    # Path Actions
    def start_add_path(self):
        if len(self.app.forest_graph.trees) < 2:
            messagebox.showwarning("Warning", "At least 2 trees are needed.", parent=self.root)
            return
        self.add_path_mode = True
        self.canvas.path_start = None
        self.app.status_bar.set_text("🖱️ Click the first tree...")
        self.control_panel.add_path_btn.config(text="✖ Exit", command=self.exit_add_path, style='Red.TButton')
    
    def exit_add_path(self):
        self.add_path_mode = False
        self.canvas.path_start = None
        self.app.status_bar.set_text("Ready")
        self.control_panel.add_path_btn.config(text="🔗 Add Path", command=self.start_add_path, style='Modern.TButton')
        self.app.update_display()
        
    def handle_path_point_selection(self, x, y):
        clicked_tree = self.app.canvas_handler._find_tree_at_position(x, y)
        if not clicked_tree: return

        if self.canvas.path_start is None:
            self.canvas.path_start = clicked_tree
            self.app.status_bar.set_text(f"🖱️ Tree {clicked_tree.tree_id} selected. Click the second tree.")
        else:
            if self.canvas.path_start != clicked_tree:
                # Automatically calculate distance for the new path
                pos1 = self.app.tree_positions[self.canvas.path_start.tree_id]
                pos2 = self.app.tree_positions[clicked_tree.tree_id]
                distance = np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)
                self.app.forest_graph.add_path(Path(self.canvas.path_start, clicked_tree, distance))
                self.app.status_bar.set_text(f"✅ Path {self.canvas.path_start.tree_id}-{clicked_tree.tree_id} added with distance {distance:.1f}.")
                self.canvas.path_start = None
            else:
                self.app.status_bar.set_text("⚠️ Cannot connect a tree to itself.")
        self.app.update_display()

    def start_delete_path(self):
        # Check if there are any paths
        has_paths = any(len(neighbors) > 0 for neighbors in self.app.forest_graph.adj_list.values())
        if not has_paths:
            messagebox.showwarning("Warning", "No paths to delete.", parent=self.root)
            return
        self.delete_path_mode = True
        self.app.status_bar.set_text("🖱️ Click a path to delete...")
        self.control_panel.delete_path_btn.config(text="✖ Exit", command=self.exit_delete_path, style='Red.TButton')

    def exit_delete_path(self):
        self.delete_path_mode = False
        self.app.status_bar.set_text("Ready")
        self.control_panel.delete_path_btn.config(text="✂️ Delete Path", command=self.start_delete_path, style='Modern.TButton')
        
    def _clear_path_highlight(self):
        """Clear the shortest path highlight and update the display."""
        self.canvas._shortest_path_highlight = []
        self.app.update_display()

    def delete_path_at_position(self, x, y):
        path_to_delete = self.app.canvas_handler.find_path_at_position(x, y)
        if path_to_delete:
            self.app.forest_graph.remove_path(path_to_delete.tree1.tree_id, path_to_delete.tree2.tree_id)
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Path deleted.")

    def find_shortest_path(self):
        if len(self.app.forest_graph.trees) < 2:
            messagebox.showwarning("Warning", "At least 2 trees are needed.", parent=self.root)
            return
        
        dialog = ShortestPathDialog(self.root, list(self.app.forest_graph.trees.keys()))
        result = dialog.show()
        
        if result:
            start_id, end_id = result
            path, dist = find_shortest_path(self.app.forest_graph, start_id, end_id)
            
            if dist == float('inf'):
                self.canvas._shortest_path_highlight = []
                self.app.update_display()
                messagebox.showinfo("No Path", "No path found between the selected trees.", parent=self.root)
                self.app.status_bar.set_text("❌ No path found")
            else:
                # Highlight the path in the canvas
                self.canvas._shortest_path_highlight = path
                self.app.update_display()
                
                # Show path information in status bar and in a popup
                path_str = " → ".join(map(str, path))
                self.app.status_bar.set_text(f"🔵 Shortest path: {path_str} (Distance: {dist:.2f})")
                
                # Display the path in a popup - when this closes, the path highlight will be cleared
                try:
                    # Create info dialog and clear path highlight when closed
                    result = messagebox.showinfo("Path Found", 
                                            f"Shortest Path: {path_str}\nDistance: {dist:.2f}", 
                                            parent=self.root)
                    # Clear highlight immediately after dialog is closed
                    self._clear_path_highlight()
                except Exception:
                    # Also clear highlight if exception occurs
                    self._clear_path_highlight()

    # Data Actions
    def load_data(self):
        dialog = LoadDataDialog(self.root)
        result = dialog.show()
        if not result:
            return
        tree_file, path_file = result
        try:
            self.app.forest_graph = load_forest_from_files(tree_file, path_file)
            self.app.tree_positions.clear()

            trees = list(self.app.forest_graph.trees.keys())
            n_trees = len(trees)
            if n_trees == 0:
                self.app.update_display()
                self.app.status_bar.set_text("✅ No trees to display.")
                return

            # Build weight mapping from adjacency list
            weights = {}
            for tree1_id, neighbors in self.app.forest_graph.adj_list.items():
                for tree2_id, weight in neighbors.items():
                    weights[(tree1_id, tree2_id)] = weight

            # Use the force-directed layout algorithm
            positions = force_directed_layout(
                trees=trees,
                adj_list=self.app.forest_graph.adj_list,
                weights=weights,
                canvas_size=(100, 100),
                iterations=400,
                min_distance=20
            )
            self.app.tree_positions = positions

            # Calculate layout quality
            total_error = 0
            has_paths = any(len(neighbors) > 0 for neighbors in self.app.forest_graph.adj_list.values())
            if has_paths:
                for tree1_id, neighbors in self.app.forest_graph.adj_list.items():
                    for tree2_id, weight in neighbors.items():
                        if tree1_id < tree2_id:  # Only process each edge once
                            x1, y1 = positions[tree1_id]
                            x2, y2 = positions[tree2_id]
                            # Actual visual distance
                            actual_dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                            # Original non-normalized weight
                            desired_dist = weight
                            
                            # Calculate proportional error
                            error = abs(actual_dist - desired_dist) / max(desired_dist, 0.1)
                            total_error += error
            
            # Create a snapshot of the original imported data
            self.app.create_snapshot()
            
            # Enable the restore original data button
            self.control_panel.restore_original_btn.config(state='normal')
            
            self.app.update_display()
            self.app.status_bar.set_text("✅ Data loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}", parent=self.root)

    def restore_original_data(self):
        """Restore the forest data to its original state from the snapshot."""
        if not self.app.has_snapshot:
            messagebox.showwarning("Warning", "No original data snapshot available.", parent=self.root)
            return
            
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Restore", 
            "This will revert all changes back to the original imported data. Continue?",
            parent=self.root
        )
        
        if not confirm:
            return
            
        if self.app.restore_snapshot():
            self.app.status_bar.set_text("✅ Forest data restored to original imported state.")
        else:
            self.app.status_bar.set_text("❌ Failed to restore original data.")

    def save_data(self):
        if not self.app.forest_graph.trees:
            messagebox.showwarning("Warning", "No data to save.", parent=self.root)
            return

        try:
            # Ask for tree file path, default name: trees.csv
            tree_file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Trees Data As...",
                initialfile="trees.csv"
            )
            if not tree_file_path:
                self.app.status_bar.set_text("⚠️ Save cancelled.")
                return

            # Ask for path file path, default name: paths.csv
            path_file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Paths Data As...",
                initialfile="paths.csv"
            )
            if not path_file_path:
                self.app.status_bar.set_text("⚠️ Save cancelled.")
                return

            # Save tree data
            with open(tree_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['tree_id', 'species', 'age', 'health_status'])
                for tree in self.app.forest_graph.trees.values():
                    writer.writerow([tree.tree_id, tree.species, tree.age, tree.health_status.name])
            
            # Save path data
            with open(path_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['tree_id1', 'tree_id2', 'distance'])
                # Get path data from adjacency list
                for tree1_id, neighbors in self.app.forest_graph.adj_list.items():
                    for tree2_id, weight in neighbors.items():
                        # Only save each edge once (undirected graph)
                        if tree1_id < tree2_id:
                            writer.writerow([tree1_id, tree2_id, weight])

            self.app.status_bar.set_text(f"✅ Data saved successfully.")
            messagebox.showinfo("Success", "Data saved successfully!", parent=self.root)

        except Exception as e:
            self.app.status_bar.set_text(f"❌ Error saving data: {e}")
            messagebox.showerror("Error", f"Failed to save data: {e}", parent=self.root)

    def clear_data(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all data?"):
            self.app.forest_graph.clear()
            self.app.tree_positions.clear()
            self.canvas.selected_tree = None
            self.add_path_mode = False
            self.delete_path_mode = False
            self.infection_sim_mode = False
            self.canvas.path_start = None
            self.delete_tree_mode = False
            self.canvas._shortest_path_highlight = []
            self.canvas._infection_highlight = set()
            self.canvas._infection_edge_highlight = set()
            self.canvas._infection_labels = {}
            
            # Clear snapshot data
            self.app.has_snapshot = False
            self.app.snapshot_forest_graph = None
            self.app.snapshot_tree_positions = None
            self.control_panel.restore_original_btn.config(state=tk.DISABLED)
            
            # Reset all control panel buttons
            self.control_panel.add_path_btn.config(text="🔗 Add Path", command=self.start_add_path, style='Modern.TButton')
            self.control_panel.delete_path_btn.config(text="✂️ Delete Path", command=self.start_delete_path, style='Modern.TButton')
            self.control_panel.delete_tree_btn.config(text="✖ Delete Tree", command=self.start_delete_tree, style='Modern.TButton')
            self.control_panel.infection_sim_btn.config(text="🦠 Infection Sim", command=self.enter_infection_sim_mode, style='Modern.TButton')
            self.app.status_bar.set_text("✅ Data cleared.")
            self.app.update_display()

    # Simulation and Analysis
    def enter_infection_sim_mode(self):
        self.infection_sim_mode = True
        self.app._pre_infection_health = {tid: t.health_status for tid, t in self.app.forest_graph.trees.items()}
        self.app.status_bar.set_text("🦠 Click an INFECTED tree to start simulation.")
        self.control_panel.infection_sim_btn.config(text="✖ Exit Sim", command=self.exit_infection_sim_mode, style='Red.TButton')
        
    def exit_infection_sim_mode(self):
        self.infection_sim_mode = False
        if self.app._pre_infection_health:
            for tid, status in self.app._pre_infection_health.items():
                if tid in self.app.forest_graph.trees:
                    self.app.forest_graph.trees[tid].health_status = status
        self.app.status_bar.set_text("Ready")
        self.control_panel.infection_sim_btn.config(text="🦠 Infection Sim", command=self.enter_infection_sim_mode, style='Modern.TButton')
        self.canvas._infection_highlight = set()
        self.app.update_display()

    def start_infection_at_position(self, x, y):
        tree = self.app.canvas_handler._find_tree_at_position(x, y)
        if tree and tree.health_status == HealthStatus.INFECTED:
            self._animate_infection(tree.tree_id)
        else:
            self.app.status_bar.set_text("⚠️ Please click an INFECTED tree.")
            messagebox.showwarning("Warning", "Please click an INFECTED tree to start simulation.", parent=self.root)
            
    def _animate_infection(self, start_tree_id):
        """
        Animate infection spread with time proportional to distance.
        The animation speed is slower for longer distances.
        """
        from ...algorithms.infection_simulation import simulate_infection
        import time
        
        # Get infection order with timing information
        infection_order = simulate_infection(self.app.forest_graph, start_tree_id)
        if not infection_order:
            self.app.status_bar.set_text("⚠️ Infection simulation failed.")
            return
        
        # Sort by infection time
        infection_order.sort(key=lambda x: x[2])  # Sort by days_to_infect
        
        # Extract timing information
        max_days = infection_order[-1][2] if len(infection_order) > 0 else 0
        base_delay = 0.1  # Base animation delay
        
        highlight_nodes = set()
        highlight_edges = set()
        infection_days = {}  # To track when (in days) each tree gets infected
        
        # First tree gets infected immediately
        highlight_nodes.add(start_tree_id)
        self.app.forest_graph.trees[start_tree_id].health_status = HealthStatus.INFECTED
        self.canvas._infection_highlight = set(highlight_nodes)
        self.canvas._infection_labels = {start_tree_id: "🦠"}
        self.app.update_display()
        self.app.root.update()
        time.sleep(base_delay)
        
        # Now infect the rest, proportional to distance
        prev_days = 0
        for idx, (tid, from_id, days) in enumerate(infection_order):
            if idx == 0:  # Skip the first tree (start tree)
                infection_days[tid] = 0
                continue
            
            # Wait proportional to the difference in infection days
            days_diff = days - prev_days
            wait_time = base_delay + (days_diff / max_days) * 1.5  # Scale for better visualization
            time.sleep(wait_time)
            prev_days = days
            
            # Infect the tree
            self.app.forest_graph.trees[tid].health_status = HealthStatus.INFECTED
            highlight_nodes.add(tid)
            infection_days[tid] = days
            
            # Add the edge that transmitted the infection
            if from_id is not None:
                highlight_edges.add((from_id, tid))
            
            # Update the visualization
            self.canvas._infection_highlight = set(highlight_nodes)
            self.canvas._infection_edge_highlight = set(highlight_edges)
            
            # Label trees with infection symbol and days
            self.canvas._infection_labels = {
                t: ("🦠" if t == start_tree_id else f"⚡{infection_days[t]:.1f} days") 
                for t in highlight_nodes
            }
            
            self.app.update_display()
            self.app.root.update()
        
        # Show simulation summary
        self.app.status_bar.set_text(f"🦠 Infection simulation finished, infected trees: {len(infection_order)}, spread time: {max_days:.1f} days")
        
        # Wait a bit before clearing the visualization
        time.sleep(2)
        self.canvas._infection_highlight = set()
        self.canvas._infection_edge_highlight = set()
        self.canvas._infection_labels = {}
        self.app.update_display()

    def analyze_forest(self):
        """Statistics and visualization of forest data."""
        plt.rcParams['font.sans-serif'] = ['Arial']  # Use Arial for English labels
        plt.rcParams['axes.unicode_minus'] = False  # Show minus sign correctly

        if not self.app.forest_graph.trees:
            messagebox.showinfo("Data Analysis", "There are no trees in the current forest.", parent=self.root)
            return
        health_counts = Counter(t.health_status.name for t in self.app.forest_graph.trees.values())
        species_counts = Counter(t.species for t in self.app.forest_graph.trees.values())
        infected_count = health_counts.get("INFECTED", 0)
        total = len(self.app.forest_graph.trees)
        infected_percent = (infected_count / total) * 100 if total else 0
        from ...algorithms.reserve_detection import find_reserves
        reserves = find_reserves(self.app.forest_graph)
        reserve_count = len(reserves)
        max_reserve = max((len(r) for r in reserves), default=0)
        most_common_species, most_common_count = ('N/A', 0) if not species_counts else species_counts.most_common(1)[0]
        # Plot
        fig, axs = plt.subplots(1, 3, figsize=(15, 4))
        color_map = {'HEALTHY': '#2ecc71', 'INFECTED': '#e74c3c', 'AT_RISK': '#f39c12'}
        pie_colors = [color_map.get(k, '#95a5a6') for k in health_counts.keys()]
        axs[0].pie(health_counts.values(), labels=health_counts.keys(), autopct='%1.1f%%', colors=pie_colors)
        axs[0].set_title('Health Status Distribution')
        axs[1].bar(species_counts.keys(), species_counts.values(), color='#3498db')
        axs[1].set_title('Species Distribution')
        axs[1].set_ylabel('Count')
        axs[1].tick_params(axis='x', rotation=30)
        axs[2].axis('off')
        summary = (f"Infection rate: {infected_percent:.1f}%\n"
                   f"Number of reserves: {reserve_count}\n"
                   f"Largest reserve size: {max_reserve}\n"
                   f"Most common species: {most_common_species} ({most_common_count})")
        axs[2].text(0.1, 0.5, summary, fontsize=13, va='center', ha='left', wrap=True)
        plt.tight_layout()
        plt.show()
        plt.close(fig)
        self.app.status_bar.set_text("📊 Forest analysis displayed.")