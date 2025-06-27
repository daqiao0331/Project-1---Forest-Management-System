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

from ...components.tree import Tree
from ...components.path import Path
from ...components.health_status import HealthStatus
from ...components.dataset_loader import load_forest_from_files
from ...algorithms.pathfinding import find_shortest_path
from ..dialogs.tree_dialogs import AddTreeDialog, DeleteTreeDialog, ModifyHealthDialog
from ..dialogs.path_dialogs import ShortestPathDialog
from ..dialogs.data_dialog import LoadDataDialog

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
        if result is None:
            return
        
        tree_id = max([t.tree_id for t in self.app.forest_graph.trees.values()], default=0) + 1
        tree = Tree(tree_id, result["species"], result["age"], result["health"])
        self.app.forest_graph.add_tree(tree)
        self.app.tree_positions[tree_id] = (random.uniform(10, 90), random.uniform(10, 90))
        self.app.update_display()
        self.app.status_bar.set_text(f"✅ Tree {tree_id} added.")

    def delete_tree(self):
        if not self.app.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees to delete.", parent=self.root)
            return
        
        tree_ids = list(self.app.forest_graph.trees.keys())
        dialog = DeleteTreeDialog(self.root, tree_ids)
        tree_id = dialog.show()
        
        if tree_id and tree_id in self.app.forest_graph.trees:
            self.app.forest_graph.remove_tree(tree_id)
            if tree_id in self.app.tree_positions:
                del self.app.tree_positions[tree_id]
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Tree {tree_id} deleted.")

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
        self.app.status_bar.set_text("🖱️ Click first tree...")
        self.control_panel.add_path_btn.config(text="❌ Exit", command=self.exit_add_path, style='Red.TButton')
    
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
            self.app.status_bar.set_text(f"🖱️ Tree {clicked_tree.tree_id} selected. Click second tree.")
        else:
            if self.canvas.path_start != clicked_tree:
                pos1 = self.app.tree_positions[self.canvas.path_start.tree_id]
                pos2 = self.app.tree_positions[clicked_tree.tree_id]
                distance = np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)
                self.app.forest_graph.add_path(Path(self.canvas.path_start, clicked_tree, distance))
                self.app.status_bar.set_text(f"✅ Path {self.canvas.path_start.tree_id}-{clicked_tree.tree_id} added.")
                self.canvas.path_start = None
            else:
                self.app.status_bar.set_text("⚠️ Cannot connect a tree to itself.")
        self.app.update_display()

    def start_delete_path(self):
        if not self.app.forest_graph.paths:
            messagebox.showwarning("Warning", "No paths to delete.", parent=self.root)
            return
        self.delete_path_mode = True
        self.app.status_bar.set_text("🖱️ Click a path to delete...")
        self.control_panel.delete_path_btn.config(text="❌ Exit", command=self.exit_delete_path, style='Red.TButton')

    def exit_delete_path(self):
        self.delete_path_mode = False
        self.app.status_bar.set_text("Ready")
        self.control_panel.delete_path_btn.config(text="✂️ Delete Path", command=self.start_delete_path, style='Modern.TButton')

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
            else:
                self.canvas._shortest_path_highlight = path
                self.app.update_display()
                messagebox.showinfo("Path Found", f"Path: {path}\nDistance: {dist:.2f}", parent=self.root)
            self.app.status_bar.set_text(f"🔵 Shortest Path: {dist:.2f}")

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
            for tree_id in self.app.forest_graph.trees:
                self.app.tree_positions[tree_id] = (random.uniform(10, 90), random.uniform(10, 90))
            self.app.update_display()
            self.app.status_bar.set_text("✅ Data loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}", parent=self.root)

    def save_data(self):
        if not self.app.forest_graph.trees:
            messagebox.showwarning("Warning", "No data to save.", parent=self.root)
            return

        try:
            # Ask for tree file path
            tree_file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Trees Data As..."
            )
            if not tree_file_path:
                self.app.status_bar.set_text("⚠️ Save cancelled.")
                return

            # Ask for path file path
            path_file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Paths Data As..."
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
                for path in self.app.forest_graph.paths:
                    writer.writerow([path.tree1.tree_id, path.tree2.tree_id, path.weight])

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
            self.exit_add_path()
            self.exit_delete_path()
            self.exit_infection_sim_mode()
            self.app.update_display()
            self.app.status_bar.set_text("✅ Data cleared.")

    # Simulation and Analysis
    def enter_infection_sim_mode(self):
        self.infection_sim_mode = True
        self.app._pre_infection_health = {tid: t.health_status for tid, t in self.app.forest_graph.trees.items()}
        self.app.status_bar.set_text("🦠 Click an INFECTED tree to start simulation.")
        self.control_panel.infection_sim_btn.config(text="❌ Exit Sim", command=self.exit_infection_sim_mode, style='Red.TButton')
        
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
            
    def _animate_infection(self, start_tree_id):
        """ Simulate and animate the infection spread starting from a given tree ID."""
        from ...algorithms.infection_simulation import simulate_infection
        import time
        infection_order = simulate_infection(self.app.forest_graph, start_tree_id)
        if not infection_order:
            self.app.status_bar.set_text("⚠️ failed")
            return
        highlight_nodes = set()
        highlight_edges = set()
        for idx, (tid, from_id) in enumerate(infection_order):
            self.app.forest_graph.trees[tid].health_status = HealthStatus.INFECTED
            highlight_nodes.add(tid)
            if from_id is not None:
                highlight_edges.add((from_id, tid))
            self.canvas._infection_highlight = set(highlight_nodes)
            self.canvas._infection_edge_highlight = set(highlight_edges)
            self.canvas._infection_labels = {tid: ("🦠" if idx==0 else "⚡") for tid, _ in infection_order[:idx+1]}
            self.app.update_display()
            self.app.root.update()
            time.sleep(0.3)
        self.app.status_bar.set_text(f"🦠 Infection simulation complete, infected trees: {len(infection_order)}")
        self.canvas._infection_highlight = set()
        self.canvas._infection_edge_highlight = set()
        self.canvas._infection_labels = {}
        self.app.update_display()

    def analyze_forest(self):
        """Analyze the forest data and visualize it."""
        plt.rcParams['font.sans-serif'] = ['SimHei']  # for Chinese label display
        plt.rcParams['axes.unicode_minus'] = False  # for negative sign display

        if not self.app.forest_graph.trees:
            messagebox.showinfo("data analysis", "The forest has no trees.", parent=self.root)
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
        # plot
        fig, axs = plt.subplots(1, 3, figsize=(15, 4))
        color_map = {'HEALTHY': '#2ecc71', 'INFECTED': '#e74c3c', 'AT_RISK': '#f39c12'}
        pie_colors = [color_map.get(k, '#95a5a6') for k in health_counts.keys()]
        axs[0].pie(health_counts.values(), labels=health_counts.keys(), autopct='%1.1f%%', colors=pie_colors)
        axs[0].set_title('health status distribution')
        axs[1].bar(species_counts.keys(), species_counts.values(), color='#3498db')
        axs[1].set_title('species distribution')
        axs[1].set_ylabel('count')
        axs[1].tick_params(axis='x', rotation=30)
        axs[2].axis('off')
        summary = (f"Infection Rate: {infected_percent:.1f}%\n"
                   f"Reserve Count: {reserve_count}\n"
                   f"Max Reserve Size: {max_reserve}\n"
                   f"Most Common Species: {most_common_species} ({most_common_count})")
        axs[2].text(0.1, 0.5, summary, fontsize=13, va='center', ha='left', wrap=True)
        plt.tight_layout()
        plt.show()
        plt.close(fig)
        self.app.status_bar.set_text("📊 Forest analysis has been displayed.")