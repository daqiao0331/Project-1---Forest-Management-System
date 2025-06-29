"""
The forest visualization canvas panel.
"""
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle, Rectangle
import numpy as np
from matplotlib.figure import Figure

class ForestCanvas:
    """Manages the Matplotlib canvas for displaying the forest."""
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#ffffff')
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))  # Increase left padding for more canvas space
 
        self.legend_frame = tk.Frame(self.frame, bg='#ffffff')
        self.legend_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 30), pady=(150, 30))  # Adjust padding for better positioning
        legend_title = tk.Label(self.legend_frame, text="Legend", font=('Segoe UI', 23, 'bold'), fg='#2c3e50', bg='#ffffff')
        legend_title.pack(pady=(0, 15))

        # Tree status legend section
        tree_section = tk.Frame(self.legend_frame, bg='#ffffff')
        tree_section.pack(fill=tk.X, pady=(0, 20))
        
        tree_title = tk.Label(tree_section, text="Tree Status", font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
        tree_title.pack(anchor=tk.W, pady=(0, 10))

        # Add legend item
        def add_legend_item(parent, emoji, text, color):
            row = tk.Frame(parent, bg='#ffffff')
            row.pack(pady=5, fill=tk.X)  
            tk.Label(row, text=emoji, font=('Segoe UI', 24), fg=color, bg='#ffffff').pack(side=tk.LEFT)
            tk.Label(row, text=text, font=('Segoe UI', 14), fg='#2c3e50', bg='#ffffff', padx=10).pack(side=tk.LEFT)

        add_legend_item(tree_section, "🌲", "Healthy(GREEN)", "#2ecc71")
        add_legend_item(tree_section, "🌴", "At Risk(YELLOW)", "#f39c12")
        add_legend_item(tree_section, "🌳", "Infected(RED)", "#e74c3c")
        
        # Path colors legend section
        path_section = tk.Frame(self.legend_frame, bg='#ffffff')
        path_section.pack(fill=tk.X, pady=(0, 20))
        
        path_title = tk.Label(path_section, text="Path Colors", font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
        path_title.pack(anchor=tk.W, pady=(0, 10))
        
        def add_path_legend(parent, color, thickness, text):
            row = tk.Frame(parent, bg='#ffffff')
            row.pack(pady=5, fill=tk.X)
            
            # Create a small canvas for the line
            line_canvas = tk.Canvas(row, width=30, height=20, bg='#ffffff', highlightthickness=0)
            line_canvas.create_line(5, 10, 25, 10, fill=color, width=thickness)
            line_canvas.pack(side=tk.LEFT)
            
            tk.Label(row, text=text, font=('Segoe UI', 14), fg='#2c3e50', bg='#ffffff', padx=10).pack(side=tk.LEFT)
        
        add_path_legend(path_section, "#95a5a6", 2, "Normal Path")
        add_path_legend(path_section, "#2980b9", 4, "Shortest Path")
        add_path_legend(path_section, "#e74c3c", 5, "Infection Path")
        
        # Areas legend section
        area_section = tk.Frame(self.legend_frame, bg='#ffffff')
        area_section.pack(fill=tk.X, pady=(0, 20))
        
        area_title = tk.Label(area_section, text="Areas", font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
        area_title.pack(anchor=tk.W, pady=(0, 10))
        
        def add_area_legend(parent, color, alpha, text):
            row = tk.Frame(parent, bg='#ffffff')
            row.pack(pady=5, fill=tk.X)
            
            # Create a small canvas for the area
            area_canvas = tk.Canvas(row, width=30, height=20, bg='#ffffff', highlightthickness=0)
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            rgb = f'#{r:02x}{g:02x}{b:02x}'
            area_canvas.create_rectangle(5, 5, 25, 15, fill=rgb, outline="", width=0)
            area_canvas.pack(side=tk.LEFT)
            
            tk.Label(row, text=text, font=('Segoe UI', 14), fg='#2c3e50', bg='#ffffff', padx=10).pack(side=tk.LEFT)
        
        add_area_legend(area_section, "#7ed6df", 0.18, "Forest Reserve")
        
        # Numbers legend section
        number_section = tk.Frame(self.legend_frame, bg='#ffffff')
        number_section.pack(fill=tk.X)
        
        number_title = tk.Label(number_section, text="Numbers", font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#ffffff')
        number_title.pack(anchor=tk.W, pady=(0, 10))
        
        number_row = tk.Frame(number_section, bg='#ffffff')
        number_row.pack(pady=5, fill=tk.X)
        
        tk.Label(number_row, text="10.5", font=('Segoe UI', 14), fg='#2c3e50', bg='#ffffff', 
                 padx=5, relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT)
        tk.Label(number_row, text="Distance between trees", font=('Segoe UI', 14), 
                 fg='#2c3e50', bg='#ffffff', padx=10).pack(side=tk.LEFT)
        
        viz_title = tk.Label(self.frame, text="🌲 Forest Visualization", 
                             font=('Segoe UI', 14, 'bold'),
                             fg='#2c3e50', bg='#ffffff')
        viz_title.pack(pady=(5, 10))

        plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(16, 10), dpi=100, facecolor='#ffffff')  # 16*100=1600, 10*100=1000
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  
        
        # Interaction state variables
        self.selected_tree = None
        self._shortest_path_highlight = []
        self._infection_highlight = set()
        self.path_start = None
        self._tooltip = None

    def setup_canvas_bindings(self, handler):
        """Bind mouse events to the canvas event handler."""
        self.canvas.mpl_connect('button_press_event', handler.on_press)
        self.canvas.mpl_connect('motion_notify_event', handler.on_motion)
        self.canvas.mpl_connect('button_release_event', handler.on_release)

    def _get_emoji_font(self):
        """Find a suitable emoji font on the system."""
        import matplotlib.font_manager as fm
        for font in ['Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji']:
            if font in [f.name for f in fm.fontManager.ttflist]:
                return font
        return 'DejaVu Sans'

    def draw_forest(self, forest_graph, tree_positions):
        """Draws the entire forest, including trees, paths, and reserves."""
        from forest_management_system.data_structures.health_status import HealthStatus
        from forest_management_system.algorithms.reserve_detection import find_reserves

        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2, color='#bdc3c7')
        self.ax.set_facecolor('#f8f9fa')
        
        # Draw Reserves
        reserves = find_reserves(forest_graph)
        for reserve in reserves:
            positions = [tree_positions[tree_id] for tree_id in reserve if tree_id in tree_positions]
            if len(positions) >= 2:
                xs, ys = zip(*positions)
                center_x, center_y = sum(xs) / len(xs), sum(ys) / len(ys)
                radius = max(np.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in positions) + 18
                self.ax.add_patch(Circle((center_x, center_y), radius, color='#7ed6df', alpha=0.18, zorder=0))
                
                # Add reserve label
                self.ax.text(center_x, center_y - radius - 5, f"Reserve ({len(reserve)} trees)", 
                             ha='center', va='bottom', fontsize=10, color='#2c3e50',
                             bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7, ec='#7ed6df'))
        
        # Get all path weights for comparison and drawing
        path_weights = [path.weight for path in forest_graph.paths]
        max_weight = max(path_weights) if path_weights else 1
        min_weight = min(path_weights) if path_weights else 1
        
        # Draw Paths
        for path in forest_graph.paths:
            if path.tree1.tree_id in tree_positions and path.tree2.tree_id in tree_positions:
                x1, y1 = tree_positions[path.tree1.tree_id]
                x2, y2 = tree_positions[path.tree2.tree_id]
                
                # Calculate visual distance versus actual weight
                visual_dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                norm_weight = (path.weight - min_weight) / (max_weight - min_weight) if max_weight > min_weight else 0.5
                
                is_shortest = any((path.tree1.tree_id == self._shortest_path_highlight[i] and path.tree2.tree_id == self._shortest_path_highlight[i+1]) or \
                                  (path.tree2.tree_id == self._shortest_path_highlight[i] and path.tree1.tree_id == self._shortest_path_highlight[i+1]) for i in range(len(self._shortest_path_highlight)-1))
                is_infection = hasattr(self, '_infection_edge_highlight') and ((path.tree1.tree_id, path.tree2.tree_id) in getattr(self, '_infection_edge_highlight', set()) or (path.tree2.tree_id, path.tree1.tree_id) in getattr(self, '_infection_edge_highlight', set()))
                
                # Use uniform line color and thickness
                color = '#e74c3c' if is_infection else ('#2980b9' if is_shortest else '#95a5a6')
                
                # Use fixed thickness, not varying by weight
                lw = 5 if is_infection else (4 if is_shortest else 2)
                
                alpha = 1.0 if is_infection else (0.9 if is_shortest else 0.7)
                self.ax.plot([x1, x2], [y1, y2], color=color, alpha=alpha, linewidth=lw, zorder=1)
                
                if is_infection:
                    dx, dy = x2-x1, y2-y1
                    arr_x, arr_y = x1 + dx*0.6, y1 + dy*0.6
                    self.ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2), zorder=2)
                
                # Calculate label position
                mx, my = (x1+x2)/2, (y1+y2)/2
                
                # Display weight with uniform background color
                self.ax.text(mx, my, f'{path.weight:.1f}', fontsize=12, color='#2c3e50', zorder=10, 
                           bbox=dict(fc='white', alpha=0.7, boxstyle='round,pad=0.2', ec='#95a5a6', lw=0.5))

        # Draw Trees
        health_colors = {HealthStatus.HEALTHY: '#2ecc71', HealthStatus.INFECTED: '#e74c3c', HealthStatus.AT_RISK: '#f39c12'}
        emoji_font = self._get_emoji_font()
        for tree_id, tree in forest_graph.trees.items():
            if tree_id in tree_positions:
                x, y = tree_positions[tree_id]
                is_selected = (self.selected_tree and self.selected_tree.tree_id == tree_id)
                label = getattr(self, '_infection_labels', {}).get(tree_id, None)
                if label:
                    emoji = label
                    color = '#e74c3c'
                else:
                    emoji = {"HEALTHY": "🌲", "INFECTED": "🌳", "AT_RISK": "🌴"}[tree.health_status.name]
                    color = health_colors[tree.health_status]
                self.ax.text(x, y, emoji, ha='center', va='center', fontsize=30 if is_selected else 25,
                             fontfamily=emoji_font, color=color, zorder=3,
                             bbox=dict(boxstyle='circle,pad=0.2', fc='white' if is_selected else 'none', ec='blue' if is_selected else 'none', lw=2, alpha=0.5))
                self.ax.text(x, y - 12, str(tree_id), ha='center', va='top', fontsize=10, fontweight='bold', color='#2c3e50', zorder=4)

        # Draw selection circle for path drawing
        if self.path_start and self.path_start.tree_id in tree_positions:
            x, y = tree_positions[self.path_start.tree_id]
            self.ax.add_patch(Circle((x, y), 8, color='#3498db', alpha=0.3, zorder=2))

        self.canvas.draw()

    def show_tooltip(self, x, y, text):
        self.hide_tooltip()
        self._tooltip = self.ax.annotate(text, xy=(x, y), xytext=(15, 15), textcoords='offset points',
                                         bbox=dict(boxstyle='round,pad=0.5', fc='#ffffe0', alpha=0.95), zorder=100)
        self.canvas.draw_idle()

    def hide_tooltip(self):
        if self._tooltip:
            try:
                # Safely remove the tooltip without using remove()
                self._tooltip.set_visible(False)
                self._tooltip = None
                self.canvas.draw_idle()
            except Exception:
                self._tooltip = None 