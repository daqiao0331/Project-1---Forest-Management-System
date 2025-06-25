import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import numpy as np
import random
import sys
import os
from forest_management_system.algorithms.infection_simulation import simulate_infection
from forest_management_system.algorithms.pathfinding import find_shortest_path
from forest_management_system.algorithms.reserve_detection import find_reserves

# ----------- 优化import路径处理 -------------
# 兼容直接运行和作为包导入
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CUR_DIR, '..'))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    from forest_management_system.components.forest_graph import ForestGraph
    from forest_management_system.components.tree import Tree
    from forest_management_system.components.path import Path
    from forest_management_system.components.health_status import HealthStatus
except ImportError as e:
    # 兼容直接在项目根目录下运行
    sys.path.insert(0, os.path.abspath(os.path.join(PARENT_DIR, '..')))
    from forest_management_system.components.forest_graph import ForestGraph
    from forest_management_system.components.tree import Tree
    from forest_management_system.components.path import Path
    from forest_management_system.components.health_status import HealthStatus
# ----------- END 优化import路径处理 -------------

class ModernButton(ttk.Button):
    """Custom modern button with better styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style='Modern.TButton')

class ForestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌲 Forest Management System")
        self.root.geometry("1600x1000")  # 增大窗口尺寸
        self.root.configure(bg='#f0f0f0')
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('Modern.TButton', 
                       padding=(10, 5), 
                       font=('Segoe UI', 9, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
        style.configure('Modern.TLabelframe', 
                       background='#ffffff',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TLabelframe.Label', 
                       font=('Segoe UI', 10, 'bold'),
                       foreground='#2c3e50',
                       background='#ffffff')
        
        # Initialize forest graph
        self.forest_graph = ForestGraph()
        self.tree_positions = {}  # Store tree positions
        self.selected_tree = None
        self.drawing_path = False
        self.path_start = None
        
        # 拖拽相关变量
        self.dragging = False
        self.drag_tree = None
        self.drag_start_pos = None
        
        # emoji字体
        self.emoji_font = self.get_emoji_font() if hasattr(self, 'get_emoji_font') else 'Segoe UI Emoji'
        
        # Health status color mapping
        self.health_colors = {
            HealthStatus.HEALTHY: '#2ecc71',
            HealthStatus.INFECTED: '#e74c3c',
            HealthStatus.AT_RISK: '#f39c12'
        }
        
        self.setup_ui()
        self.setup_canvas()
        
    def setup_ui(self):
        # Create main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title bar
        title_frame = tk.Frame(main_container, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🌲 Forest Management System", 
                              font=('Segoe UI', 16, 'bold'),
                              fg='white', 
                              bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main content area
        content_frame = tk.Frame(main_container, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar - Control Panel
        sidebar_frame = tk.Frame(content_frame, bg='#ffffff', width=300)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        sidebar_frame.pack_propagate(False)
        
        # Scrollable sidebar
        sidebar_canvas = tk.Canvas(sidebar_frame, bg='#ffffff', highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_frame, orient="vertical", command=sidebar_canvas.yview)
        scrollable_frame = tk.Frame(sidebar_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        )
        
        sidebar_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        # Tree Operations Section
        tree_frame = ttk.LabelFrame(scrollable_frame, text="🌳 Tree Operations", 
                                   style='Modern.TLabelframe', padding=15)
        tree_frame.pack(fill=tk.X, pady=(0, 15))
        
        ModernButton(tree_frame, text="➕  Add Tree", 
                    command=self.add_tree_dialog).pack(fill=tk.X, pady=3)
        ModernButton(tree_frame, text="❌  Delete Tree", 
                    command=self.remove_tree).pack(fill=tk.X, pady=3)
        ModernButton(tree_frame, text="🔧  Modify Health", 
                    command=self.change_health_status).pack(fill=tk.X, pady=3)
        
        # Path Operations Section
        path_frame = ttk.LabelFrame(scrollable_frame, text="🛤️ Path Operations", 
                                   style='Modern.TLabelframe', padding=15)
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.add_path_btn = ModernButton(path_frame, text="🔗  Add Path", command=self.start_add_path, style='Modern.TButton')
        self.add_path_btn.pack(fill=tk.X, pady=3)
        ModernButton(path_frame, text="✂️  Delete Path", 
                    command=self.remove_path_dialog).pack(fill=tk.X, pady=3)
        ModernButton(path_frame, text="🔵  Shortest Path", 
                    command=self.shortest_path_dialog).pack(fill=tk.X, pady=3)
        
        # Data Operations Section
        data_frame = ttk.LabelFrame(scrollable_frame, text="💾 Data Operations", 
                                   style='Modern.TLabelframe', padding=15)
        data_frame.pack(fill=tk.X, pady=(0, 15))
        
        ModernButton(data_frame, text="📂  Load Data", 
                    command=self.load_data).pack(fill=tk.X, pady=3)
        ModernButton(data_frame, text="💾  Save Data", 
                    command=self.save_data).pack(fill=tk.X, pady=3)
        ModernButton(data_frame, text="❌  Clear Data", 
                    command=self.clear_data).pack(fill=tk.X, pady=3)
        ModernButton(data_frame, text="🦠  Infection Sim", 
                    command=self.infection_simulation_dialog).pack(fill=tk.X, pady=3)
        
        # Forest Information Section
        info_frame = ttk.LabelFrame(scrollable_frame, text="📊 Forest Information", 
                                   style='Modern.TLabelframe', padding=15)
        info_frame.pack(fill=tk.X)
        
        # Create a styled text widget
        self.info_text = tk.Text(info_frame, height=12, width=35, 
                                font=('Consolas', 9),
                                bg='#f8f9fa', fg='#2c3e50',
                                relief='flat', borderwidth=1,
                                padx=10, pady=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Pack sidebar components
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Right side - Visualization Area
        viz_frame = tk.Frame(content_frame, bg='#ffffff')
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Visualization title
        viz_title = tk.Label(viz_frame, text="🌲 Forest Visualization", 
                            font=('Segoe UI', 14, 'bold'),
                            fg='#2c3e50', bg='#ffffff')
        viz_title.pack(pady=(0, 10))
        
        # Create matplotlib figure with modern styling
        plt.style.use('default')
        self.fig, self.ax = plt.subplots(figsize=(14, 10), facecolor='#ffffff')  # 增大画布尺寸
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind mouse events
        self.canvas.mpl_connect('button_press_event', self.on_canvas_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_canvas_hover)
        self.canvas.mpl_connect('button_release_event', self.on_canvas_release)
        
        # Status bar
        self.status_bar = tk.Label(main_container, text="Ready", 
                                  relief=tk.SUNKEN, anchor=tk.W,
                                  font=('Segoe UI', 9),
                                  bg='#ecf0f1', fg='#2c3e50')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # Initialize display
        self.update_display()
        
    def setup_canvas(self):
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.2, color='#bdc3c7')
        self.ax.set_facecolor('#f8f9fa')
        self.ax.set_title("Forest Visualization", fontsize=14, fontweight='bold', color='#2c3e50')
        
        # Remove spines
        for spine in self.ax.spines.values():
            spine.set_color('#bdc3c7')
            spine.set_linewidth(0.5)
        
    def add_tree_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Add New Tree")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text="Add New Tree", 
                              font=('Segoe UI', 16, 'bold'),
                              fg='#2c3e50', bg='#f0f0f0')
        title_label.pack(pady=(30, 30))
        
        # Form frame
        form_frame = tk.Frame(dialog, bg='#f0f0f0')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Species
        tk.Label(form_frame, text="Species:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        species_var = tk.StringVar(value="Pine")
        species_entry = ttk.Entry(form_frame, textvariable=species_var, 
                                 font=('Segoe UI', 11), width=35)
        species_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Age
        tk.Label(form_frame, text="Age:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        age_var = tk.StringVar(value="10")
        age_entry = ttk.Entry(form_frame, textvariable=age_var, 
                             font=('Segoe UI', 11), width=35)
        age_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Health Status
        tk.Label(form_frame, text="Health Status:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        health_var = tk.StringVar(value="HEALTHY")
        health_combo = ttk.Combobox(form_frame, textvariable=health_var, 
                                   values=["HEALTHY", "INFECTED", "AT_RISK"],
                                   font=('Segoe UI', 11), width=32)
        health_combo.pack(fill=tk.X, pady=(0, 30))
        
        # Buttons frame
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        def add_tree():
            try:
                species = species_var.get()
                age = int(age_var.get())
                health = HealthStatus[health_var.get()]
                
                # Generate random position
                x = random.uniform(10, 90)
                y = random.uniform(10, 90)
                
                # Generate unique ID
                tree_id = max([t.tree_id for t in self.forest_graph.trees.values()], default=0) + 1
                
                tree = Tree(tree_id, species, age, health)
                self.forest_graph.add_tree(tree)
                self.tree_positions[tree_id] = (x, y)
                
                dialog.destroy()
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"✅ Tree {tree_id} added successfully")
                
            except ValueError as e:
                messagebox.showerror("Error", f"Input error: {e}")
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        ttk.Button(button_frame, text="Add Tree", command=add_tree, 
                  style='Modern.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
        
    def remove_tree(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees to delete")
            return
            
        tree_ids = list(self.forest_graph.trees.keys())
        tree_id = simpledialog.askinteger("Delete Tree", 
                                        f"Select tree ID to delete:\n{tree_ids}",
                                        minvalue=min(tree_ids), 
                                        maxvalue=max(tree_ids))
        
        if tree_id and tree_id in self.forest_graph.trees:
            self.forest_graph.remove_tree(tree_id)
            if tree_id in self.tree_positions:
                del self.tree_positions[tree_id]
            self.update_display()
            self.update_info()
            self.status_bar.config(text=f"✅ Tree {tree_id} deleted successfully")
        elif tree_id:
            messagebox.showerror("Error", "Invalid tree ID")
            
    def change_health_status(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees available")
            return
            
        tree_ids = list(self.forest_graph.trees.keys())
        tree_id = simpledialog.askinteger("Modify Health Status", 
                                        f"Select tree ID:\n{tree_ids}",
                                        minvalue=min(tree_ids), 
                                        maxvalue=max(tree_ids))
        
        if tree_id and tree_id in self.forest_graph.trees:
            health_var = tk.StringVar(value="HEALTHY")
            dialog = tk.Toplevel(self.root)
            dialog.title("🔧 Modify Health Status")
            dialog.geometry("300x200")
            dialog.configure(bg='#f0f0f0')
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"300x200+{x}+{y}")
            
            tk.Label(dialog, text="Select new health status:", 
                    font=('Segoe UI', 12, 'bold'),
                    fg='#2c3e50', bg='#f0f0f0').pack(pady=20)
            
            health_combo = ttk.Combobox(dialog, textvariable=health_var, 
                                       values=["HEALTHY", "INFECTED", "AT_RISK"],
                                       font=('Segoe UI', 10), width=20)
            health_combo.pack(pady=10)
            
            def change_status():
                try:
                    health = HealthStatus[health_var.get()]
                    self.forest_graph.update_health_status(tree_id, health)
                    dialog.destroy()
                    self.update_display()
                    self.update_info()
                    self.status_bar.config(text=f"✅ Health status of tree {tree_id} updated")
                except ValueError as e:
                    messagebox.showerror("Error", f"Input error: {e}")
            
            ttk.Button(dialog, text="Update", command=change_status, 
                      style='Modern.TButton').pack(pady=20)
        elif tree_id:
            messagebox.showerror("Error", "Invalid tree ID")
            
    def start_add_path(self):
        if len(self.forest_graph.trees) < 2:
            messagebox.showwarning("Warning", "At least 2 trees are needed to add a path")
            return
        self.drawing_path = True
        self.path_start = None
        self.status_bar.config(text="🖱️ Click two trees to connect, or click Exit to cancel")
        # 按钮切换为Exit
        self.add_path_btn.config(text="❌  Exit", command=self.exit_add_path, style='Red.TButton')
        style = ttk.Style()
        style.configure('Red.TButton', background='#e74c3c', foreground='white', font=('Segoe UI', 9, 'bold'))
        
    def exit_add_path(self):
        self.drawing_path = False
        self.path_start = None
        self.status_bar.config(text="Ready")
        # 按钮切换回Add Path
        self.add_path_btn.config(text="🔗  Add Path", command=self.start_add_path, style='Modern.TButton')
        
    def remove_path_dialog(self):
        if not self.forest_graph.paths:
            messagebox.showwarning("Warning", "No paths to delete")
            return
            
        tree_ids = list(self.forest_graph.trees.keys())
        tree_id1 = simpledialog.askinteger("Delete Path", 
                                         f"Select first tree ID:\n{tree_ids}",
                                         minvalue=min(tree_ids), 
                                         maxvalue=max(tree_ids))
        
        if tree_id1 and tree_id1 in self.forest_graph.trees:
            tree_id2 = simpledialog.askinteger("Delete Path", 
                                             f"Select second tree ID:\n{tree_ids}",
                                             minvalue=min(tree_ids), 
                                             maxvalue=max(tree_ids))
            
            if tree_id2 and tree_id2 in self.forest_graph.trees:
                self.forest_graph.remove_path(tree_id1, tree_id2)
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"✅ Path {tree_id1} - {tree_id2} deleted successfully")
            elif tree_id2:
                messagebox.showerror("Error", "Invalid second tree ID")
        elif tree_id1:
            messagebox.showerror("Error", "Invalid first tree ID")
            
    def on_canvas_click(self, event):
        if event.inaxes != self.ax:
            return
        if self.drawing_path:
            clicked_tree = self.find_tree_at_position(event.xdata, event.ydata)
            if clicked_tree:
                if self.path_start is None:
                    self.path_start = clicked_tree
                    self.status_bar.config(text=f"🖱️ First tree {clicked_tree.tree_id} selected, now click the second tree or Exit")
                else:
                    if self.path_start != clicked_tree:
                        x1, y1 = self.tree_positions[self.path_start.tree_id]
                        x2, y2 = self.tree_positions[clicked_tree.tree_id]
                        distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                        path = Path(self.path_start, clicked_tree, distance)
                        self.forest_graph.add_path(path)
                        self.update_display()
                        self.update_info()
                        self.status_bar.config(text=f"✅ Path {self.path_start.tree_id} - {clicked_tree.tree_id} added successfully. Click two more trees or Exit.")
                        self.path_start = None
                    else:
                        self.status_bar.config(text="⚠️ Cannot connect a tree to itself")
            else:
                self.status_bar.config(text="⚠️ Please click on a tree position or Exit")
            return
        clicked_tree = self.find_tree_at_position(event.xdata, event.ydata)
        if clicked_tree:
            self.selected_tree = clicked_tree
            self.update_display()
            self.status_bar.config(text=f"ℹ️ Tree {clicked_tree.tree_id} selected - drag to move")
            self.dragging = True
            self.drag_tree = clicked_tree
            self.drag_start_pos = (event.xdata, event.ydata)
        else:
            self.selected_tree = None
            self.update_display()
            self.status_bar.config(text="Ready")
        
    def find_tree_at_position(self, x, y):
        for tree_id, (tx, ty) in self.tree_positions.items():
            if tree_id in self.forest_graph.trees:
                distance = np.sqrt((x-tx)**2 + (y-ty)**2)
                if distance <= 15:  # 增大点击半径以适应更大的树符号
                    return self.forest_graph.trees[tree_id]
        return None
        
    def update_display(self):
        self.ax.clear()
        self.setup_canvas()
        
        # Draw paths
        for path in self.forest_graph.paths:
            x1, y1 = self.tree_positions[path.tree1.tree_id]
            x2, y2 = self.tree_positions[path.tree2.tree_id]
            if hasattr(self, '_shortest_path_highlight') and self._shortest_path_highlight:
                sp = self._shortest_path_highlight
                for i in range(len(sp)-1):
                    if (path.tree1.tree_id == sp[i] and path.tree2.tree_id == sp[i+1]) or (path.tree2.tree_id == sp[i] and path.tree1.tree_id == sp[i+1]):
                        self.ax.plot([x1, x2], [y1, y2], color='#2980b9', alpha=0.9, linewidth=4, zorder=10)
                        break
                else:
                    self.ax.plot([x1, x2], [y1, y2], color='#95a5a6', alpha=0.6, linewidth=2)
            else:
                self.ax.plot([x1, x2], [y1, y2], color='#95a5a6', alpha=0.6, linewidth=2)
        
        # Draw trees
        for tree_id, tree in self.forest_graph.trees.items():
            if tree_id in self.tree_positions:
                x, y = self.tree_positions[tree_id]
                # emoji
                if tree.health_status == HealthStatus.HEALTHY:
                    tree_emoji = "🌲"
                elif tree.health_status == HealthStatus.INFECTED:
                    tree_emoji = "🌳"
                else:
                    tree_emoji = "🌴"
                if hasattr(self, '_infection_highlight') and tree_id in self._infection_highlight:
                    tree_emoji = "🦠"
                    fontsize = 30 if tree == self.selected_tree else 25
                    alpha = 1.0
                else:
                    fontsize = 30 if tree == self.selected_tree else 25
                    alpha = 1.0 if tree == self.selected_tree else 0.9
                self.ax.text(x, y, tree_emoji, ha='center', va='center', 
                           fontsize=fontsize, alpha=alpha, 
                           weight='bold' if tree == self.selected_tree else 'normal',
                           color=self.health_colors[tree.health_status],
                           fontfamily=self.emoji_font)
                self.ax.text(x, y-12, str(tree_id), ha='center', va='top', 
                           fontsize=10, fontweight='bold', color='#2c3e50',
                           bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#2c3e50', alpha=0.9))
        
        # Draw path start point (if drawing path)
        if self.drawing_path and self.path_start:
            x, y = self.tree_positions[self.path_start.tree_id]
            circle = Circle((x, y), 8, color='#3498db', alpha=0.3, linewidth=2, 
                           edgecolor='#2980b9', fill=False)
            self.ax.add_patch(circle)
        
        # 清理高亮状态
        if hasattr(self, '_infection_highlight') and self._infection_highlight:
            pass
        else:
            self._infection_highlight = set()
        if hasattr(self, '_shortest_path_highlight') and self._shortest_path_highlight:
            pass
        else:
            self._shortest_path_highlight = []
        
        # 图例
        legend_x = 105
        legend_y_start = 55
        self.ax.text(legend_x, legend_y_start, "Tree Status Legend", 
                    fontsize=14, fontweight='bold', color='#2c3e50',
                    ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 18, "🌲", fontsize=24, color='#2ecc71',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 18, "Healthy Tree", 
                    fontsize=12, color='#2c3e50', ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 32, "🌳", fontsize=24, color='#e74c3c',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 32, "Infected Tree", 
                    fontsize=12, color='#2c3e50', ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 46, "🌴", fontsize=24, color='#f39c12',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 46, "At Risk Tree", 
                    fontsize=12, color='#2c3e50', ha='left', va='top')
        self.canvas.draw()
        
    def update_info(self):
        self.info_text.delete(1.0, tk.END)
        # Statistics
        tree_count = len(self.forest_graph.trees)
        path_count = len(self.forest_graph.paths)
        # 最大保护区和感染树百分比
        try:
            reserves = find_reserves(self.forest_graph)
            max_reserve = max((len(r) for r in reserves), default=0)
        except Exception:
            max_reserve = 0
        infected_count = sum(1 for t in self.forest_graph.trees.values() if t.health_status.name == "INFECTED")
        infected_percent = (infected_count / tree_count * 100) if tree_count else 0
        info = f"🌲 FOREST STATISTICS\n"
        info += "="*30 + "\n"
        info += f"📊 Tree Count: {tree_count}\n"
        info += f"🛤️ Path Count: {path_count}\n"
        info += f"🟦 Max Reserve Size: {max_reserve}\n"
        info += f"🔴 Infected %: {infected_percent:.1f}%\n\n"
        # Health status statistics
        health_stats = {}
        for tree in self.forest_graph.trees.values():
            status = tree.health_status.name
            health_stats[status] = health_stats.get(status, 0) + 1
        info += f"🏥 HEALTH STATUS\n"
        info += "="*30 + "\n"
        for status, count in health_stats.items():
            emoji = "🟢" if status == "HEALTHY" else "🔴" if status == "INFECTED" else "🟠"
            info += f"{emoji} {status}: {count}\n"
        # Species statistics
        species_stats = {}
        for tree in self.forest_graph.trees.values():
            species = tree.species
            species_stats[species] = species_stats.get(species, 0) + 1
        info += f"\n🌳 SPECIES DISTRIBUTION\n"
        info += "="*30 + "\n"
        for species, count in species_stats.items():
            info += f"🌲 {species}: {count}\n"
        self.info_text.insert(1.0, info)

    def infection_simulation_dialog(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees available")
            return
        tree_ids = list(self.forest_graph.trees.keys())
        tree_id = simpledialog.askinteger("Infection Simulation", 
                                        f"Select start tree ID for infection:\n{tree_ids}",
                                        minvalue=min(tree_ids), 
                                        maxvalue=max(tree_ids))
        if tree_id and tree_id in self.forest_graph.trees:
            self.animate_infection(tree_id)
        elif tree_id:
            messagebox.showerror("Error", "Invalid tree ID")

    def animate_infection(self, start_tree_id):
        infected = set()
        queue = [start_tree_id]
        step = 0
        def step_func():
            nonlocal infected, queue, step
            if not queue:
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"🦠 Infection simulation finished. {len(infected)} trees infected.")
                messagebox.showinfo("Simulation Finished", f"Infection spread complete! Total infected: {len(infected)}")
                return
            current = queue.pop(0)
            if current in infected:
                self.root.after(300, step_func)
                return
            infected.add(current)
            self._infection_highlight = infected.copy()
            for neighbor in self._get_neighbors(current):
                if neighbor not in infected and self.forest_graph.trees[neighbor].health_status != HealthStatus.INFECTED:
                    queue.append(neighbor)
            self.update_display()
            self.status_bar.config(text=f"🦠 Infection step {step+1}: {len(infected)} infected")
            step += 1
            self.root.after(500, step_func)
        self._infection_highlight = set()
        step_func()

    def highlight_shortest_path(self, start_tree_id, end_tree_id):
        try:
            path, dist = find_shortest_path(self.forest_graph, start_tree_id, end_tree_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import/find shortest path: {e}")
            return
        if not path or dist == float('inf'):
            messagebox.showinfo("No Path", "No path found between the selected trees.")
            return
        self._shortest_path_highlight = path
        self.update_display()
        self.status_bar.config(text=f"🔵 Shortest path: {path}, distance: {dist:.2f}")
        messagebox.showinfo("Shortest Path", f"Path: {path}\nDistance: {dist:.2f}")

    def shortest_path_dialog(self):
        if len(self.forest_graph.trees) < 2:
            messagebox.showwarning("Warning", "At least 2 trees are needed to find a path")
            return
        tree_ids = list(self.forest_graph.trees.keys())
        start_id = simpledialog.askinteger("Shortest Path", f"Select start tree ID:\n{tree_ids}", minvalue=min(tree_ids), maxvalue=max(tree_ids))
        if start_id is None or start_id not in self.forest_graph.trees:
            messagebox.showerror("Error", "Invalid start tree ID")
            return
        end_id = simpledialog.askinteger("Shortest Path", f"Select end tree ID:\n{tree_ids}", minvalue=min(tree_ids), maxvalue=max(tree_ids))
        if end_id is None or end_id not in self.forest_graph.trees:
            messagebox.showerror("Error", "Invalid end tree ID")
            return
        if start_id == end_id:
            messagebox.showwarning("Warning", "Start and end tree cannot be the same")
            return
        self.highlight_shortest_path(start_id, end_id)

    def load_data(self):
        try:
            from tkinter import filedialog
            from forest_management_system.components.dataset_loader import load_forest_from_files
            import os
            dialog = tk.Toplevel(self.root)
            dialog.title("📂 Load Forest Data")
            dialog.geometry("800x550")
            dialog.configure(bg='#f0f0f0')
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
            y = (dialog.winfo_screenheight() // 2) - (550 // 2)
            dialog.geometry(f"800x550+{x}+{y}")
            title_label = tk.Label(dialog, text="Load Forest Data", font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='#f0f0f0')
            title_label.pack(pady=(30, 20))
            instruction_label = tk.Label(dialog, text="Please select the tree and path CSV files to load:", font=('Segoe UI', 11), fg='#2c3e50', bg='#f0f0f0')
            instruction_label.pack(pady=(0, 30))
            form_frame = tk.Frame(dialog, bg='#f0f0f0')
            form_frame.pack(fill=tk.BOTH, expand=True, padx=40)
            tree_frame = tk.Frame(form_frame, bg='#f0f0f0')
            tree_frame.pack(fill=tk.X, pady=(0, 20))
            tk.Label(tree_frame, text="🌳 Tree Data File:", font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
            tree_file_frame = tk.Frame(tree_frame, bg='#f0f0f0')
            tree_file_frame.pack(fill=tk.X)
            tree_file_var = tk.StringVar()
            tree_file_entry = ttk.Entry(tree_file_frame, textvariable=tree_file_var, font=('Segoe UI', 10), width=50)
            tree_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            def browse_tree_file():
                filename = filedialog.askopenfilename(title="Select Tree Data File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialdir=".")
                if filename:
                    tree_file_var.set(filename)
            ttk.Button(tree_file_frame, text="Browse", command=browse_tree_file).pack(side=tk.RIGHT)
            path_frame = tk.Frame(form_frame, bg='#f0f0f0')
            path_frame.pack(fill=tk.X, pady=(0, 30))
            tk.Label(path_frame, text="🛤️ Path Data File:", font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
            path_file_frame = tk.Frame(path_frame, bg='#f0f0f0')
            path_file_frame.pack(fill=tk.X)
            path_file_var = tk.StringVar()
            path_file_entry = ttk.Entry(path_file_frame, textvariable=path_file_var, font=('Segoe UI', 10), width=50)
            path_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            def browse_path_file():
                filename = filedialog.askopenfilename(title="Select Path Data File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialdir=".")
                if filename:
                    path_file_var.set(filename)
            ttk.Button(path_file_frame, text="Browse", command=browse_path_file).pack(side=tk.RIGHT)
            quick_frame = tk.Frame(form_frame, bg='#f0f0f0')
            quick_frame.pack(fill=tk.X, pady=(0, 20))
            def load_default_data():
                tree_file = os.path.abspath(os.path.join(CUR_DIR, '../../../data/forest_management_dataset-trees.csv'))
                path_file = os.path.abspath(os.path.join(CUR_DIR, '../../../data/forest_management_dataset-paths.csv'))
                if os.path.exists(tree_file) and os.path.exists(path_file):
                    tree_file_var.set(tree_file)
                    path_file_var.set(path_file)
                else:
                    messagebox.showerror("Error", "Default data files not found")
            ttk.Button(quick_frame, text="Load Default Data", command=load_default_data).pack(side=tk.LEFT)
            button_frame = tk.Frame(form_frame, bg='#f0f0f0')
            button_frame.pack(fill=tk.X)
            def load_files():
                tree_file = tree_file_var.get().strip()
                path_file = path_file_var.get().strip()
                if not tree_file or not path_file:
                    messagebox.showerror("Error", "Please select both tree and path files")
                    return
                if not os.path.exists(tree_file):
                    messagebox.showerror("Error", f"Tree file not found: {tree_file}")
                    return
                if not os.path.exists(path_file):
                    messagebox.showerror("Error", f"Path file not found: {path_file}")
                    return
                try:
                    self.forest_graph = load_forest_from_files(tree_file, path_file)
                    for tree_id in self.forest_graph.trees.keys():
                        x = random.uniform(10, 90)
                        y = random.uniform(10, 90)
                        self.tree_positions[tree_id] = (x, y)
                    dialog.destroy()
                    self.update_display()
                    self.update_info()
                    self.status_bar.config(text="✅ Data loaded successfully")
                    messagebox.showinfo("Success", f"Data loaded successfully!\nTrees: {len(self.forest_graph.trees)}\nPaths: {len(self.forest_graph.paths)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load data: {e}")
            def cancel():
                dialog.destroy()
            ttk.Button(button_frame, text="Load Data", command=load_files, style='Modern.TButton').pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file dialog: {e}")

    def save_data(self):
        # 保存到 data 目录下的 csv
        try:
            tree_file = os.path.abspath(os.path.join(CUR_DIR, '../../../data/forest_management_dataset-trees.csv'))
            path_file = os.path.abspath(os.path.join(CUR_DIR, '../../../data/forest_management_dataset-paths.csv'))
            import csv
            # 保存树
            with open(tree_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['tree_id', 'species', 'age', 'health_status'])
                for t in self.forest_graph.trees.values():
                    writer.writerow([t.tree_id, t.species, t.age, t.health_status.name])
            # 保存路径
            with open(path_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['tree_1', 'tree_2', 'distance'])
                for p in self.forest_graph.paths:
                    writer.writerow([p.tree1.tree_id, p.tree2.tree_id, p.weight])
            self.status_bar.config(text="✅ 数据保存成功")
            messagebox.showinfo("Success", "数据保存成功！")
        except Exception as e:
            messagebox.showerror("Error", f"保存数据失败: {e}")

    def clear_data(self):
        self.forest_graph = ForestGraph()
        self.tree_positions = {}
        self.selected_tree = None
        self.drawing_path = False
        self.path_start = None
        self.update_display()
        self.update_info()
        self.status_bar.config(text="✅ 数据已清空")

    def on_canvas_hover(self, event):
        # Show tooltip when hovering over a tree
        if event.inaxes != self.ax:
            self.hide_tooltip()
            return
        # If dragging, update tree position
        if self.dragging and self.drag_tree and event.button == 1:
            new_x = max(5, min(95, event.xdata))
            new_y = max(5, min(95, event.ydata))
            self.tree_positions[self.drag_tree.tree_id] = (new_x, new_y)
            self.update_display()
            self.status_bar.config(text=f"🔄 Moving Tree {self.drag_tree.tree_id} to ({new_x:.1f}, {new_y:.1f})")
            return
        hovered_tree = self.find_tree_at_position(event.xdata, event.ydata)
        if hovered_tree:
            text = (f"Tree ID: {hovered_tree.tree_id}\n"
                    f"Species: {hovered_tree.species}\n"
                    f"Age: {hovered_tree.age}\n"
                    f"Health: {hovered_tree.health_status.name}")
            self.show_tooltip(event, text)
        else:
            self.hide_tooltip()

    def on_canvas_release(self, event):
        if self.dragging and self.drag_tree:
            self.dragging = False
            final_x, final_y = self.tree_positions[self.drag_tree.tree_id]
            self.status_bar.config(text=f"✅ Tree {self.drag_tree.tree_id} moved to ({final_x:.1f}, {final_y:.1f})")
            self.drag_tree = None
            self.drag_start_pos = None
            self.update_display()
            self.update_info()

    def show_tooltip(self, event, text):
        self.hide_tooltip()
        self._tooltip = self.ax.annotate(
            text,
            xy=(event.xdata, event.ydata),
            xytext=(15, 15),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='#ffffe0', ec='#2c3e50', lw=1, alpha=0.95),
            fontsize=10,
            color='#2c3e50',
            zorder=100
        )
        self.canvas.draw_idle()

    def hide_tooltip(self):
        if hasattr(self, '_tooltip') and self._tooltip:
            try:
                self._tooltip.remove()
            except:
                try:
                    self._tooltip.set_visible(False)
                    self.ax.texts = [t for t in self.ax.texts if t != self._tooltip]
                except:
                    pass
            self._tooltip = None
            self.canvas.draw_idle()

    def get_emoji_font(self):
        import matplotlib.font_manager as fm
        emoji_fonts = [
            'Segoe UI Emoji',  # Windows
            'Apple Color Emoji',  # macOS
            'Noto Color Emoji',  # Linux/Android
            'EmojiOne Mozilla',  # Linux
            'DejaVu Sans',  # fallback
        ]
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        for font in emoji_fonts:
            if font in available_fonts:
                return font
        return 'DejaVu Sans'

    def _get_neighbors(self, tree_id):
        neighbors = set()
        for p in self.forest_graph.paths:
            if p.tree1.tree_id == tree_id:
                neighbors.add(p.tree2.tree_id)
            elif p.tree2.tree_id == tree_id:
                neighbors.add(p.tree1.tree_id)
        return list(neighbors)

def main():
    root = tk.Tk()
    app = ForestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()