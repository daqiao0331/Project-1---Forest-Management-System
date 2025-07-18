"""
Handles all mouse events on the ForestCanvas.
"""
import numpy as np
from ...data_structures.path import Path

class CanvasEventsHandler:
    def __init__(self, app_logic):
        self.app = app_logic
        self.canvas = self.app.main_window.forest_canvas
        self.dragging = False
        self.drag_tree = None

    def on_press(self, event):
        if event.inaxes != self.canvas.ax: return

        if getattr(self.app.ui_actions, 'delete_tree_mode', False):
            self.app.ui_actions.delete_tree_at_position(event.xdata, event.ydata)
            return
        if self.app.ui_actions.delete_path_mode:
            self.app.ui_actions.delete_path_at_position(event.xdata, event.ydata)
            return
        if self.app.ui_actions.infection_sim_mode:
            self.app.ui_actions.start_infection_at_position(event.xdata, event.ydata)
            return
        if self.app.ui_actions.add_path_mode:
            self.app.ui_actions.handle_path_point_selection(event.xdata, event.ydata)
            return

        clicked_tree = self._find_tree_at_position(event.xdata, event.ydata)
        if clicked_tree:
            self.canvas.selected_tree = clicked_tree
            self.dragging = True
            self.drag_tree = clicked_tree
            self.app.status_bar.set_text(f"ℹ️ Tree {clicked_tree.tree_id} selected. Drag to move.")
        else:
            self.canvas.selected_tree = None
            self.app.status_bar.set_text("Ready")
        self.app.update_display()

    def on_motion(self, event):
        if event.inaxes != self.canvas.ax:
            self.canvas.hide_tooltip()
            return

        if self.dragging and self.drag_tree and event.button == 1 and event.xdata and event.ydata:
            new_x = max(5, min(95, event.xdata))
            new_y = max(5, min(95, event.ydata))
            self.app.tree_positions[self.drag_tree.tree_id] = (new_x, new_y)
            
            # Update all path weights connected to the dragged tree in real-time
            tree_id = self.drag_tree.tree_id
            if tree_id in self.app.forest_graph.adj_list:
                for other_tree_id, _ in self.app.forest_graph.adj_list[tree_id].items():
                    # Calculate new distance based on current positions
                    pos1 = self.app.tree_positions[tree_id]
                    pos2 = self.app.tree_positions[other_tree_id]
                    new_distance = np.sqrt((pos2[0]-pos1[0])**2 + (pos2[1]-pos1[1])**2)
                    
                    # Update the path weight
                    self.app.forest_graph.update_distance(tree_id, other_tree_id, new_distance)
            
            self.app.update_display()
            self.app.status_bar.set_text(f"🔄 Moving Tree {self.drag_tree.tree_id}")
            return

        hovered_tree = self._find_tree_at_position(event.xdata, event.ydata)
        if hovered_tree:
            text = (f"ID: {hovered_tree.tree_id}\n"
                    f"Species: {hovered_tree.species}\n"
                    f"Age: {hovered_tree.age}\n"
                    f"Health: {hovered_tree.health_status.name}")
            self.canvas.show_tooltip(event.xdata, event.ydata, text)
        else:
            self.canvas.hide_tooltip()

    def on_release(self, event):
        if self.dragging and self.drag_tree:
            self.dragging = False
            self.app.status_bar.set_text(f"✅ Tree {self.drag_tree.tree_id} moved and path weights updated.")
            self.drag_tree = None
            self.app.update_display()

    def _find_tree_at_position(self, x, y):
        if x is None or y is None: return None
        for tree_id, (tx, ty) in self.app.tree_positions.items():
            if tree_id in self.app.forest_graph.trees:
                if np.sqrt((x - tx)**2 + (y - ty)**2) <= 2.5: # Smaller radius for more precise clicking
                    return self.app.forest_graph.trees[tree_id]
        return None

    def find_path_at_position(self, x, y, threshold=0.5):
        if x is None or y is None: return None
        
        # Iterate through all edges
        for tree1_id, neighbors in self.app.forest_graph.adj_list.items():
            for tree2_id, weight in neighbors.items():
                # Process each edge only once
                if tree1_id < tree2_id:
                    pos1 = self.app.tree_positions.get(tree1_id)
                    pos2 = self.app.tree_positions.get(tree2_id)
                    if not pos1 or not pos2: continue
                    
                    x1, y1 = pos1
                    x2, y2 = pos2
                    
                    dx, dy = x2 - x1, y2 - y1
                    if dx == dy == 0:
                        dist = np.sqrt((x - x1)**2 + (y - y1)**2)
                    else:
                        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx**2 + dy**2)))
                        proj_x, proj_y = x1 + t * dx, y1 + t * dy
                        dist = np.sqrt((x - proj_x)**2 + (y - proj_y)**2)
                    
                    if dist <= threshold:
                        # Create a temporary Path object to maintain interface compatibility
                        from ...data_structures.path import Path
                        tree1 = self.app.forest_graph.trees[tree1_id]
                        tree2 = self.app.forest_graph.trees[tree2_id]
                        return Path(tree1, tree2, weight)
        
        return None