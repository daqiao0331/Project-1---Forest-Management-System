import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import numpy as np
import random
import sys
import os
from forest_management_system.algorithms.pathfinding import find_shortest_path
from forest_management_system.algorithms.reserve_detection import find_reserves

# ----------- Optimize import path handling -------------
# Compatible with both direct run and package import
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
    # Also compatible with running from project root directory
    sys.path.insert(0, os.path.abspath(os.path.join(PARENT_DIR, '..')))
    from forest_management_system.components.forest_graph import ForestGraph
    from forest_management_system.components.tree import Tree
    from forest_management_system.components.path import Path
    from forest_management_system.components.health_status import HealthStatus
# ----------- END Optimize import path handling -------------

class ModernButton(ttk.Button):
    """Custom modern button with better styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style='Modern.TButton')

class ForestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🌲 Forest Management System")
        self.root.geometry("1600x1000")  
        self.root.configure(bg='#f0f0f0')
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern styles
        style.configure('Modern.TButton', 
                       padding=(18, 10), 
                       font=('Segoe UI', 15, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
        style.configure('Red.TButton', background='#e74c3c', foreground='white', font=('Segoe UI', 15, 'bold'), padding=(18, 10))
        style.map('Red.TButton', background=[('active', '#c0392b'), ('!active', '#e74c3c')])
        
        style.configure('Modern.TLabelframe', 
                       background='#ffffff',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TLabelframe.Label', 
                       font=('Segoe UI', 16, 'bold'),
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
        self.emoji_font = self.get_emoji_font()
        
        # Health status color mapping
        self.health_colors = {
            HealthStatus.HEALTHY: '#2ecc71',
            HealthStatus.INFECTED: '#e74c3c',
            HealthStatus.AT_RISK: '#f39c12'
        }
        
        self.deleting_path = False
        self.infection_sim_mode = False
        self._pre_infection_health = None
        
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
        sidebar_frame = tk.Frame(content_frame, bg='#ffffff', width=420)
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
        self.delete_path_btn = ModernButton(path_frame, text="✂️  Delete Path", command=self.remove_path_mode, style='Modern.TButton')
        self.delete_path_btn.pack(fill=tk.X, pady=3)
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
        self.infection_sim_btn = ModernButton(data_frame, text="🦠  Infection Sim", 
                    command=self.enter_infection_sim_mode)
        self.infection_sim_btn.pack(fill=tk.X, pady=3)
        ModernButton(data_frame, text="📊  Analyze Forest", command=self.show_forest_analysis).pack(fill=tk.X, pady=3)
        
        # Forest Information Section
        info_frame = ttk.LabelFrame(scrollable_frame, text="📊 Forest Information", 
                                   style='Modern.TLabelframe', padding=15)
        info_frame.pack(fill=tk.X)
        # 信息区加滚动条
        info_text_frame = tk.Frame(info_frame, bg='#ffffff')
        info_text_frame.pack(fill=tk.BOTH, expand=True)
        self.info_text = tk.Text(info_text_frame, height=22, width=35, 
                                font=('Consolas', 13),
                                bg='#f8f9fa', fg='#2c3e50',
                                relief='flat', borderwidth=1,
                                padx=10, pady=10)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 鼠标滚轮支持
        self.info_text.bind('<Enter>', lambda e: self.info_text.bind_all('<MouseWheel>', lambda event: self.info_text.yview_scroll(int(-1*(event.delta/120)), 'units')))
        self.info_text.bind('<Leave>', lambda e: self.info_text.unbind_all('<MouseWheel>'))
        
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
        self.fig, self.ax = plt.subplots(figsize=(28, 20), facecolor='#ffffff')
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
        dialog.geometry("640x480")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (640 // 2)
        y = (dialog.winfo_screenheight() // 2) - (480 // 2)
        dialog.geometry(f"640x480+{x}+{y}")
        title_label = tk.Label(dialog, text="Add New Tree", 
                              font=('Segoe UI', 16, 'bold'),
                              fg='#2c3e50', bg='#f0f0f0')
        title_label.pack(pady=(30, 30))
        form_frame = tk.Frame(dialog, bg='#f0f0f0')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        tk.Label(form_frame, text="Species:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        species_var = tk.StringVar(value="Pine")
        species_entry = ttk.Entry(form_frame, textvariable=species_var, 
                                 font=('Segoe UI', 11), width=35)
        species_entry.pack(fill=tk.X, pady=(0, 20))
        tk.Label(form_frame, text="Age:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        age_var = tk.StringVar(value="10")
        age_entry = ttk.Entry(form_frame, textvariable=age_var, 
                             font=('Segoe UI', 11), width=35)
        age_entry.pack(fill=tk.X, pady=(0, 20))
        tk.Label(form_frame, text="Health Status:", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='#f0f0f0').pack(anchor='w', pady=(0, 8))
        health_var = tk.StringVar(value="HEALTHY")
        health_combo = ttk.Combobox(form_frame, textvariable=health_var, 
                                   values=["HEALTHY", "INFECTED", "AT_RISK"],
                                   font=('Segoe UI', 11), width=32)
        health_combo.pack(fill=tk.X, pady=(0, 30))
        button_frame = tk.Frame(form_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        def add_tree():
            try:
                species = species_var.get()
                age = int(age_var.get())
                health = HealthStatus[health_var.get()]
                x = random.uniform(10, 90)
                y = random.uniform(10, 90)
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
        ttk.Button(button_frame, text="Add Tree", command=add_tree, 
                  style='Modern.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        
    def remove_tree(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees to delete")
            return
        tree_ids = list(self.forest_graph.trees.keys())
        # 自定义大弹窗
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Tree")
        dialog.geometry("480x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"480x300+{x}+{y}")
        tk.Label(dialog, text="Select tree ID to delete:", font=('Segoe UI', 20, 'bold'), bg='#f0f0f0').pack(pady=(36, 10))
        tk.Label(dialog, text=f"Available: {tree_ids}", font=('Segoe UI', 15), bg='#f0f0f0').pack(pady=(0, 10))
        id_var = tk.StringVar()
        id_entry = ttk.Entry(dialog, textvariable=id_var, font=('Segoe UI', 17), width=18)
        id_entry.pack(pady=(0, 18))
        def on_ok():
            try:
                tree_id = int(id_var.get())
            except Exception:
                messagebox.showerror("Error", "Please enter a valid integer ID")
                return
            if tree_id in self.forest_graph.trees:
                self.forest_graph.remove_tree(tree_id)
                if tree_id in self.tree_positions:
                    del self.tree_positions[tree_id]
                dialog.destroy()
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"✅ Tree {tree_id} deleted successfully")
            else:
                messagebox.showerror("Error", "Invalid tree ID")
        btn_frame = tk.Frame(dialog, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Delete", command=on_ok, width=12, style='Gray.TButton').pack(side=tk.LEFT, padx=16)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12, style='Gray.TButton').pack(side=tk.LEFT)
        
    def change_health_status(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees available")
            return
        tree_ids = list(self.forest_graph.trees.keys())
        dialog = tk.Toplevel(self.root)
        dialog.title("Modify Health Status")
        dialog.geometry("480x300")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"480x300+{x}+{y}")
        tk.Label(dialog, text="Select tree ID to modify:", font=('Segoe UI', 15, 'bold'), bg='#f0f0f0').pack(pady=(36, 10))
        tk.Label(dialog, text=f"Available: {tree_ids}", font=('Segoe UI', 11), bg='#f0f0f0').pack(pady=(0, 10))
        id_var = tk.StringVar()
        id_entry = ttk.Entry(dialog, textvariable=id_var, font=('Segoe UI', 13), width=18)
        id_entry.pack(pady=(0, 18))
        tk.Label(dialog, text="New health status:", font=('Segoe UI', 11, 'bold'), bg='#f0f0f0').pack(pady=(0, 8))
        health_var = tk.StringVar(value="HEALTHY")
        health_combo = ttk.Combobox(dialog, textvariable=health_var, 
                                   values=["HEALTHY", "INFECTED", "AT_RISK"],
                                   font=('Segoe UI', 11), width=16)
        health_combo.pack(pady=(0, 18))
        def on_ok():
            try:
                tree_id = int(id_var.get())
            except Exception:
                messagebox.showerror("Error", "Please enter a valid integer ID")
                return
            if tree_id in self.forest_graph.trees:
                health = HealthStatus[health_var.get()]
                self.forest_graph.update_health_status(tree_id, health)
                dialog.destroy()
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"✅ Health status of tree {tree_id} updated")
            else:
                messagebox.showerror("Error", "Invalid tree ID")
        btn_frame = tk.Frame(dialog, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        btn_frame.pack_configure(padx=40)  # 增加左侧内边距
        ttk.Button(btn_frame, text="Update", command=on_ok, width=12, style='Gray.TButton').pack(side=tk.LEFT, padx=16)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12, style='Gray.TButton').pack(side=tk.LEFT)
        
    def start_add_path(self):
        if len(self.forest_graph.trees) < 2:
            messagebox.showwarning("Warning", "At least 2 trees are needed to add a path")
            return
        self.drawing_path = True
        self.path_start = None
        self.status_bar.config(text="🖱️ Click two trees to connect, or click Exit to cancel")
        self.add_path_btn.config(text="❌  Exit", command=self.exit_add_path, style='Red.TButton')
        
    def exit_add_path(self):
        self.drawing_path = False
        self.path_start = None
        self.status_bar.config(text="Ready")
        self.add_path_btn.config(text="🔗  Add Path", command=self.start_add_path, style='Modern.TButton')
        
    def remove_path_mode(self):
        if not self.forest_graph.paths:
            messagebox.showwarning("Warning", "No paths to delete")
            return
        self.deleting_path = True
        self.status_bar.config(text="🖱️  Click any path to delete, or click Exit to quit.")
        self.delete_path_btn.config(text="❌  Exit", command=self.exit_remove_path_mode, style='Red.TButton')

    def exit_remove_path_mode(self):
        self.deleting_path = False
        self.status_bar.config(text="Ready")
        self.delete_path_btn.config(text="✂️  Delete Path", command=self.remove_path_mode, style='Modern.TButton')

    def on_canvas_click(self, event):
        if event.inaxes != self.ax:
            return
        # 删除路径模式
        if hasattr(self, 'deleting_path') and self.deleting_path:
            clicked_path = self.find_path_at_position(event.xdata, event.ydata)
            if clicked_path:
                self.forest_graph.remove_path(clicked_path.tree1.tree_id, clicked_path.tree2.tree_id)
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"✅ Path {clicked_path.tree1.tree_id} - {clicked_path.tree2.tree_id} deleted. Continue clicking or Exit to quit.")
            else:
                self.status_bar.config(text="⚠️  Please click a path or click Exit to quit.")
            return
        # 感染模拟模式下，点击infected树直接开始感染
        if getattr(self, 'infection_sim_mode', False):
            clicked_tree = self.find_tree_at_position(event.xdata, event.ydata)
            if clicked_tree and clicked_tree.health_status.name == "INFECTED":
                self.animate_infection(clicked_tree.tree_id)
                return
            else:
                self.status_bar.config(text="🦠 Please click an INFECTED tree to start simulation, or click Exit to quit.")
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

    def find_path_at_position(self, x, y, threshold=3):
        # 判断(x, y)是否在某条路径附近，threshold为像素距离
        for path in self.forest_graph.paths:
            x1, y1 = self.tree_positions[path.tree1.tree_id]
            x2, y2 = self.tree_positions[path.tree2.tree_id]
            # 计算点到线段的距离
            px, py = x, y
            dx, dy = x2 - x1, y2 - y1
            if dx == dy == 0:
                dist = ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
            else:
                t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
                proj_x = x1 + t * dx
                proj_y = y1 + t * dy
                dist = ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5
            if dist <= threshold:
                return path
        return None
        
    def update_display(self):
        self.ax.clear()
        self.setup_canvas()
        # Draw reserves (as one big circle per reserve)
        reserves = find_reserves(self.forest_graph)
        reserve_color = '#7ed6df'
        for reserve in reserves:
            positions = [self.tree_positions[tree_id] for tree_id in reserve if tree_id in self.tree_positions]
            if len(positions) >= 2:
                xs, ys = zip(*positions)
                center_x = sum(xs) / len(xs)
                center_y = sum(ys) / len(ys)
                # 计算最大距离作为半径
                max_r = max(np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) for x, y in positions) + 18
                self.ax.add_patch(Circle((center_x, center_y), max_r, color=reserve_color, alpha=0.18, zorder=2, linewidth=0))
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
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            self.ax.text(mx, my, f"{distance:.2f}", fontsize=12, color='#34495e', ha='center', va='center', bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='#bbb', alpha=0.7), zorder=20)
        # Draw trees
        for tree_id, tree in self.forest_graph.trees.items():
            if tree_id in self.tree_positions:
                x, y = self.tree_positions[tree_id]
                if tree.health_status == HealthStatus.HEALTHY:
                    tree_emoji = "🌲"
                    color = self.health_colors[HealthStatus.HEALTHY]
                elif tree.health_status == HealthStatus.INFECTED:
                    tree_emoji = "🌳"
                    color = '#e74c3c'
                else:
                    tree_emoji = "🌴"
                    color = '#f39c12'
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
                           color=color,
                           fontfamily=self.emoji_font)
                self.ax.text(x, y-12, str(tree_id), ha='center', va='top', 
                           fontsize=10, fontweight='bold', color='#2c3e50',
                           bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#2c3e50', alpha=0.9))
        if self.drawing_path and self.path_start:
            x, y = self.tree_positions[self.path_start.tree_id]
            circle = Circle((x, y), 8, color='#3498db', alpha=0.3, linewidth=2, 
                           edgecolor='#2980b9', fill=False)
            self.ax.add_patch(circle)
        if hasattr(self, '_infection_highlight') and self._infection_highlight:
            pass
        else:
            self._infection_highlight = set()
        if hasattr(self, '_shortest_path_highlight') and self._shortest_path_highlight:
            pass
        else:
            self._shortest_path_highlight = []
        legend_x = 105
        legend_y_start = 55
        self.ax.text(legend_x, legend_y_start, "Tree Status Legend", 
                    fontsize=14, fontweight='bold', color='#2c3e50',
                    ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 18, "🌲", fontsize=24, color='#2ecc71',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 18, "Healthy Tree", 
                    fontsize=12, color='#2c3e50', ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 32, "🌴", fontsize=24, color='#f39c12',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 32, "At Risk Tree", 
                    fontsize=12, color='#2c3e50', ha='left', va='top')
        self.ax.text(legend_x, legend_y_start - 46, "🌳", fontsize=24, color='#e74c3c',
                    ha='left', va='top', fontfamily=self.emoji_font)
        self.ax.text(legend_x + 16, legend_y_start - 46, "Infected Tree", 
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

    def enter_infection_sim_mode(self):
        if not self.forest_graph.trees:
            messagebox.showwarning("Warning", "No trees available")
            return
        self.infection_sim_mode = True
        # 保存所有树的健康状态
        self._pre_infection_health = {tid: t.health_status for tid, t in self.forest_graph.trees.items()}
        self.infection_sim_btn.config(text="❌  Exit", command=self.exit_infection_sim_mode, style='Red.TButton')
        self.status_bar.config(text="🦠 Infection Sim Mode: Click an INFECTED tree to start simulation, or click Exit to quit.")

    def exit_infection_sim_mode(self):
        self.infection_sim_mode = False
        # 恢复所有树的健康状态
        if self._pre_infection_health is not None:
            for tid, status in self._pre_infection_health.items():
                if tid in self.forest_graph.trees:
                    self.forest_graph.trees[tid].health_status = status
        self._pre_infection_health = None
        self._infection_highlight = set()
        self.update_display()
        self.update_info()
        self.infection_sim_btn.config(text="🦠  Infection Sim", command=self.enter_infection_sim_mode, style='Modern.TButton')
        self.status_bar.config(text="Ready")

    def infection_simulation_dialog(self):
        if self.infection_sim_mode:
            # 模式下直接弹窗
            tree_ids = [tid for tid, t in self.forest_graph.trees.items() if t.health_status.name == "INFECTED"]
            if not tree_ids:
                messagebox.showwarning("Warning", "No INFECTED trees available to start infection.")
                return
            dialog = tk.Toplevel(self.root)
            dialog.title("Infection Simulation")
            dialog.geometry("480x300")
            dialog.configure(bg='#f0f0f0')
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"480x300+{x}+{y}")
            tk.Label(dialog, text="Select start tree ID for infection:", font=('Segoe UI', 20, 'bold'), bg='#f0f0f0').pack(pady=(36, 10))
            tk.Label(dialog, text=f"Available: {tree_ids}", font=('Segoe UI', 15), bg='#f0f0f0').pack(pady=(0, 10))
            id_var = tk.StringVar()
            id_entry = ttk.Entry(dialog, textvariable=id_var, font=('Segoe UI', 17), width=18)
            id_entry.pack(pady=(0, 18))
            def on_ok():
                try:
                    tree_id = int(id_var.get())
                except Exception:
                    messagebox.showerror("Error", "Please enter a valid integer ID")
                    return
                if tree_id in tree_ids:
                    dialog.destroy()
                    self.animate_infection(tree_id)
                else:
                    messagebox.showerror("Error", "Invalid tree ID. Please select an INFECTED tree.")
            btn_frame = tk.Frame(dialog, bg='#f0f0f0')
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Start", command=on_ok, width=12, style='Gray.TButton').pack(side=tk.LEFT, padx=16)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12, style='Gray.TButton').pack(side=tk.LEFT)
        else:
            # 非模式下，保持原有行为
            if not self.forest_graph.trees:
                messagebox.showwarning("Warning", "No trees available")
                return
            tree_ids = [tid for tid, t in self.forest_graph.trees.items() if t.health_status.name == "INFECTED"]
            if not tree_ids:
                messagebox.showwarning("Warning", "No INFECTED trees available to start infection.")
                return
            dialog = tk.Toplevel(self.root)
            dialog.title("Infection Simulation")
            dialog.geometry("480x300")
            dialog.configure(bg='#f0f0f0')
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"480x300+{x}+{y}")
            tk.Label(dialog, text="Select start tree ID for infection:", font=('Segoe UI', 20, 'bold'), bg='#f0f0f0').pack(pady=(36, 10))
            tk.Label(dialog, text=f"Available: {tree_ids}", font=('Segoe UI', 15), bg='#f0f0f0').pack(pady=(0, 10))
            id_var = tk.StringVar()
            id_entry = ttk.Entry(dialog, textvariable=id_var, font=('Segoe UI', 17), width=18)
            id_entry.pack(pady=(0, 18))
            def on_ok():
                try:
                    tree_id = int(id_var.get())
                except Exception:
                    messagebox.showerror("Error", "Please enter a valid integer ID")
                    return
                if tree_id in tree_ids:
                    dialog.destroy()
                    self.animate_infection(tree_id)
                else:
                    messagebox.showerror("Error", "Invalid tree ID. Please select an INFECTED tree.")
            btn_frame = tk.Frame(dialog, bg='#f0f0f0')
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Start", command=on_ok, width=12, style='Gray.TButton').pack(side=tk.LEFT, padx=16)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12, style='Gray.TButton').pack(side=tk.LEFT)

    def animate_infection(self, start_tree_id):
        import heapq
        infected = set()
        # (预计传播时间, 距离, health优先级, 当前树id, 来源树id)
        queue = []
        heapq.heappush(queue, (0, 0, 0, start_tree_id, None))
        step = 0
        def health_priority(tree):
            if self.forest_graph.trees[tree].health_status == HealthStatus.AT_RISK:
                return 0
            return 1  # HEALTHY
        def get_edge_weight(t1, t2):
            for p in self.forest_graph.paths:
                if (p.tree1.tree_id == t1 and p.tree2.tree_id == t2) or (p.tree2.tree_id == t1 and p.tree1.tree_id == t2):
                    return p.weight
            return float('inf')
        def step_func():
            nonlocal infected, queue, step
            if not queue:
                self.update_display()
                self.update_info()
                self.status_bar.config(text=f"🦠 Infection simulation finished. {len(infected)} trees infected.")
                messagebox.showinfo("Simulation Finished", f"Infection spread complete! Total infected: {len(infected)}")
                return
            # 取出传播时间最早的树
            cur_time, dist, hprio, current, from_tree = heapq.heappop(queue)
            if current in infected:
                self.root.after(10, step_func)
                return
            infected.add(current)
            # 传播后健康状态变为INFECTED
            if self.forest_graph.trees[current].health_status != HealthStatus.INFECTED:
                self.forest_graph.trees[current].health_status = HealthStatus.INFECTED
            self._infection_highlight = infected.copy()
            # 只允许INFECTED树传播
            if self.forest_graph.trees[current].health_status == HealthStatus.INFECTED:
                neighbors = self.forest_graph.get_neighbors(current)
                # 过滤未感染的邻居
                uninfected_neighbors = [n for n in neighbors if n not in infected and self.forest_graph.trees[n].health_status != HealthStatus.INFECTED]
                # 按距离和health优先级排序
                neighbor_info = []
                for n in uninfected_neighbors:
                    w = get_edge_weight(current, n)
                    hprio = health_priority(n)
                    neighbor_info.append((w, hprio, n))
                neighbor_info.sort()  # 距离小优先，AT RISK优先
                for w, hprio, n in neighbor_info:
                    # 传播时间 = 距离/5*0.1
                    spread_time = cur_time + (w / 5.0) * 0.1
                    heapq.heappush(queue, (spread_time, w, hprio, n, current))
            self.update_display()
            self.status_bar.config(text=f"🦠 Infection step {step+1}: {len(infected)} infected")
            step += 1
            # 下一个传播时间
            if queue:
                next_time = queue[0][0]
                delay = max(1, int((next_time - cur_time) * 1000))
            else:
                delay = 500
            self.root.after(delay, step_func)
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
        # 弹窗，两个输入框
        dialog = tk.Toplevel(self.root)
        dialog.title("Shortest Path")
        dialog.geometry("540x340")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Start Tree ID:", font=('Segoe UI', 14, 'bold'), bg='#f0f0f0').pack(pady=(38, 8))
        start_var = tk.StringVar()
        start_entry = ttk.Entry(dialog, textvariable=start_var, font=('Segoe UI', 14), width=22)
        start_entry.pack(pady=(0, 12))
        tk.Label(dialog, text="End Tree ID:", font=('Segoe UI', 14, 'bold'), bg='#f0f0f0').pack(pady=(12, 8))
        end_var = tk.StringVar()
        end_entry = ttk.Entry(dialog, textvariable=end_var, font=('Segoe UI', 14), width=22)
        end_entry.pack(pady=(0, 12))
        def on_ok():
            try:
                start_id = int(start_var.get())
                end_id = int(end_var.get())
            except Exception:
                messagebox.showerror("Error", "Please enter valid integer IDs")
                return
            if start_id not in tree_ids or end_id not in tree_ids:
                messagebox.showerror("Error", "Invalid tree ID")
                return
            if start_id == end_id:
                messagebox.showwarning("Warning", "Start and end tree cannot be the same")
                return
            dialog.destroy()
            self.highlight_shortest_path(start_id, end_id)
        btn_frame = tk.Frame(dialog, bg='#f0f0f0')
        btn_frame.pack(pady=24)
        btn_frame.pack_configure(padx=40)  # 增加左侧内边距
        ModernButton(btn_frame, text="OK", command=on_ok, width=12).pack(side=tk.LEFT, padx=18)
        ModernButton(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT)

    def load_data(self):
        try:
            from tkinter import filedialog
            from forest_management_system.components.dataset_loader import load_forest_from_files
            import os
            if not hasattr(self, 'last_csv_dir'):
                self.last_csv_dir = '.'
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
                filename = filedialog.askopenfilename(title="Select Tree Data File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialdir=self.last_csv_dir)
                if filename:
                    tree_file_var.set(filename)
                    self.last_csv_dir = os.path.dirname(filename)
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
                filename = filedialog.askopenfilename(title="Select Path Data File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialdir=self.last_csv_dir)
                if filename:
                    path_file_var.set(filename)
                    self.last_csv_dir = os.path.dirname(filename)
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
        try:
            from tkinter import filedialog
            import csv
            import os
            # 选择保存树文件
            tree_file = filedialog.asksaveasfilename(
                title="Save Tree Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="forest_management_dataset-trees.csv"
            )
            if not tree_file:
                self.status_bar.config(text="❌ Save cancelled (tree file)")
                return
            # 选择保存路径文件
            path_file = filedialog.asksaveasfilename(
                title="Save Path Data",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="forest_management_dataset-paths.csv"
            )
            if not path_file:
                self.status_bar.config(text="❌ Save cancelled (path file)")
                return
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
            self.status_bar.config(text="✅ Data saved successfully")
            messagebox.showinfo("Success", f"Data saved successfully!\nTree file: {tree_file}\nPath file: {path_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def clear_data(self):
        self.forest_graph = ForestGraph()
        self.tree_positions = {}
        self.selected_tree = None
        self.drawing_path = False
        self.path_start = None
        self._infection_highlight = set()
        self.update_display()
        self.update_info()
        self.status_bar.config(text="✅ Data cleared")

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
    
    def show_forest_analysis(self):
        # Gather statistics
        tree_count = len(self.forest_graph.trees)
        if tree_count == 0:
            messagebox.showinfo("Forest Analysis", "No trees in the forest.")
            return
        infected_count = sum(1 for t in self.forest_graph.trees.values() if t.health_status.name == "INFECTED")
        infected_percent = (infected_count / tree_count) * 100
        from collections import Counter
        # 统计健康状态
        health_counts = Counter(t.health_status.name for t in self.forest_graph.trees.values())
        # 统计物种分布
        species_counter = Counter(t.species for t in self.forest_graph.trees.values())
        if species_counter:
            most_common_species, most_common_count = species_counter.most_common(1)[0]
        else:
            most_common_species, most_common_count = 'N/A', 0
        reserves = find_reserves(self.forest_graph)
        max_reserve = max((len(r) for r in reserves), default=0)
        reserve_count = len(reserves)
        def plot_analysis():
            import matplotlib.pyplot as plt
            fig, axs = plt.subplots(1, 3, figsize=(15, 4))
            # Pie chart for health status
            color_map = {'HEALTHY': '#2ecc71', 'INFECTED': '#e74c3c', 'AT_RISK': '#f39c12'}
            pie_colors = [color_map.get(k, '#95a5a6') for k in health_counts.keys()]
            axs[0].pie(health_counts.values(), labels=health_counts.keys(), autopct='%1.1f%%', colors=pie_colors)
            axs[0].set_title('Health Status Distribution')
            # Bar chart for species
            axs[1].bar(species_counter.keys(), species_counter.values(), color='#3498db')
            axs[1].set_title('Species Distribution')
            axs[1].set_ylabel('Count')
            axs[1].tick_params(axis='x', rotation=30)
            # Text summary
            axs[2].axis('off')
            summary = (
                f"Infected: {infected_percent:.1f}%\n"
                f"Reserve Count: {reserve_count}\n"
                f"Max Reserve Size: {max_reserve}\n"
                f"Most Common Species: {most_common_species} ({most_common_count})"
            )
            axs[2].text(0.1, 0.5, summary, fontsize=13, va='center', ha='left', wrap=True)
            plt.tight_layout()
            plt.show(block=False)
            plt.close(fig)
        plot_analysis()
        self.status_bar.config(text="📊 Forest analysis displayed.")
def main():
    root = tk.Tk()
    root.title("Forest Management System")
    root.state('zoomed')  # Windows全屏
    root.resizable(True, True)
    app = ForestGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()