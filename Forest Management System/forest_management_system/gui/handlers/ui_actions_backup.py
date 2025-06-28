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
        self.control_panel.delete_tree_btn.config(text="❌ Exit", command=self.exit_delete_tree, style='Red.TButton')

    def exit_delete_tree(self):
        self.delete_tree_mode = False
        self.app.status_bar.set_text("Ready")
        self.control_panel.delete_tree_btn.config(text="🌳 Delete Tree", command=self.start_delete_tree, style='Modern.TButton')
        self.app.update_display()

    def delete_tree_at_position(self, x, y):
        tree = self.app.canvas_handler._find_tree_at_position(x, y)
        if tree:
            self.app.forest_graph.remove_tree(tree.tree_id)
            if tree.tree_id in self.app.tree_positions:
                del self.app.tree_positions[tree.tree_id]
            self.app.update_display()
            self.app.status_bar.set_text(f"✅ Tree {tree.tree_id} deleted.")

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
            self.app.status_bar.set_text(f"🖱️ Tree {clicked_tree.tree_id} selected. Click the second tree.")
        else:
            if self.canvas.path_start != clicked_tree:
                # 自动计算新路径的距离
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

    def clear_shortest_path(self):
        """Clear the shortest path highlight from the canvas and reset status bar."""
        self.canvas._shortest_path_highlight = []
        self.app.update_display()
        self.app.status_bar.set_text("🔵 Shortest path highlight cleared.")

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

            self.canvas._shortest_path_highlight = []
            self.app.update_display()

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
            
            # 创建自定义力导向布局
            import random
            import numpy as np
            from collections import defaultdict
            
            # 获取所有树的ID
            trees = list(self.app.forest_graph.trees.keys())
            n_trees = len(trees)
            
            if n_trees == 0:
                self.app.update_display()
                self.app.status_bar.set_text("✅ No trees to display.")
                return
            
            # 初始随机位置 - 更加分散在画布范围内
            positions = {}
            for tree_id in trees:
                positions[tree_id] = (
                    random.uniform(10, 90),  # x: 10-90，更宽范围
                    random.uniform(10, 90)   # y: 10-90，更宽范围
                )
            
            # 构建权重映射
            weights = {}
            for path in self.app.forest_graph.paths:
                tid1, tid2 = path.tree1.tree_id, path.tree2.tree_id
                weights[(tid1, tid2)] = weights[(tid2, tid1)] = path.weight
            
            # 将权重归一化到更大的范围，增加节点间距
            if weights:
                weight_values = list(weights.values())
                min_weight = min(weight_values)
                max_weight = max(weight_values)
                weight_range = max(max_weight - min_weight, 1)  # 避免除以零
                target_min, target_max = 15, 70  # 更大的目标范围，增大间距
                
                for key, weight in list(weights.items()):
                    normalized = target_min + (weight - min_weight) * (target_max - target_min) / weight_range
                    weights[key] = normalized
            
            # 构建邻接表
            neighbors = defaultdict(list)
            for tid1, tid2 in weights:
                neighbors[tid1].append(tid2)
                neighbors[tid2].append(tid1)
            
            # 模拟物理力进行布局
            temperature = 100.0  # 更高的初始温度，允许更大的移动
            iterations = 400     # 增加迭代次数
            
            for iteration in range(iterations):
                # 每次迭代缓慢降低温度
                temperature *= 0.98  # 降温更慢
                
                # 计算每个节点受到的合力
                forces = {tid: [0, 0] for tid in trees}
                
                # 1. 基于边权重的弹簧力（吸引/排斥）
                for tid1, tid2 in weights:
                    x1, y1 = positions[tid1]
                    x2, y2 = positions[tid2]
                    
                    # 计算当前距离
                    dx, dy = x2 - x1, y2 - y1
                    distance = max(np.sqrt(dx*dx + dy*dy), 0.01)  # 避免除以零
                    
                    # 计算基于权重的理想距离
                    ideal_distance = weights[(tid1, tid2)]
                    
                    # 计算吸引/排斥力（距离太大则吸引，太小则排斥）
                    force_factor = (distance - ideal_distance) / distance
                    
                    # 添加力到两个节点
                    fx, fy = force_factor * dx, force_factor * dy
                    forces[tid1][0] += fx
                    forces[tid1][1] += fy
                    forces[tid2][0] -= fx
                    forces[tid2][1] -= fy
                
                # 2. 所有节点间的增强排斥力（避免过于密集）
                for i, tid1 in enumerate(trees):
                    for tid2 in trees[i+1:]:
                        # 对所有节点都施加排斥力，增强分散效果
                        x1, y1 = positions[tid1]
                        x2, y2 = positions[tid2]
                        
                        dx, dy = x2 - x1, y2 - y1
                        distance = max(np.sqrt(dx*dx + dy*dy), 0.01)
                        
                        # 增大排斥力系数，更强的排斥力
                        force_factor = 200.0 / (distance * distance)  # 增大系数
                        
                        # 添加力到两个节点（相互排斥）
                        fx, fy = force_factor * dx / distance, force_factor * dy / distance
                        forces[tid1][0] -= fx
                        forces[tid1][1] -= fy
                        forces[tid2][0] += fx
                        forces[tid2][1] += fy
                
                # 3. 边界力 - 保持节点在画布内但让节点尽可能分散
                for tid in trees:
                    x, y = positions[tid]
                    
                    # 更宽松的边界控制，只在接近边缘时施加力
                    if x < 5:
                        forces[tid][0] += (5 - x) * 0.5
                    elif x > 95:
                        forces[tid][0] -= (x - 95) * 0.5
                        
                    if y < 5:
                        forces[tid][1] += (5 - y) * 0.5
                    elif y > 95:
                        forces[tid][1] -= (y - 95) * 0.5
                
                # 4. 让孤立的节点分散在画布四周
                isolated = [tid for tid in trees if not neighbors[tid]]
                if isolated:
                    # 将孤立节点放置在画布四周
                    corners = [(15, 15), (85, 15), (15, 85), (85, 85)]
                    sides = [(50, 15), (85, 50), (50, 85), (15, 50)]
                    positions_list = corners + sides
                    
                    for i, tid in enumerate(isolated):
                        if i < len(positions_list):
                            positions[tid] = positions_list[i]
                        else:
                            # 如果孤立节点太多，则随机分布
                            positions[tid] = (random.uniform(10, 90), random.uniform(10, 90))
                
                # 5. 限制移动幅度
                for tid in trees:
                    fx, fy = forces[tid]
                    # 限制力的大小
                    force_mag = np.sqrt(fx*fx + fy*fy)
                    if force_mag > temperature:
                        fx = fx * temperature / force_mag
                        fy = fy * temperature / force_mag
                    
                    # 更新位置
                    x, y = positions[tid]
                    new_x = max(5, min(95, x + fx))
                    new_y = max(5, min(95, y + fy))
                    positions[tid] = (new_x, new_y)
            
            # 最终处理：确保节点间距足够大
            min_distance = 20  # 最小节点间距
            
            for _ in range(50):  # 最多尝试50次调整
                has_overlap = False
                for i, tid1 in enumerate(trees):
                    for tid2 in trees[i+1:]:
                        x1, y1 = positions[tid1]
                        x2, y2 = positions[tid2]
                        dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                        
                        if dist < min_distance:  # 如果太近，将它们推开
                            has_overlap = True
                            angle = np.arctan2(y2 - y1, x2 - x1)
                            push_dist = (min_distance - dist) / 2
                            
                            # 将两个节点沿相反方向推开
                            positions[tid1] = (
                                max(5, min(95, x1 - push_dist * np.cos(angle))),
                                max(5, min(95, y1 - push_dist * np.sin(angle)))
                            )
                            positions[tid2] = (
                                max(5, min(95, x2 + push_dist * np.cos(angle))),
                                max(5, min(95, y2 + push_dist * np.sin(angle)))
                            )
                
                if not has_overlap:
                    break
            
            # 将计算好的位置应用到树
            self.app.tree_positions = positions
            
            # 评估布局质量
            total_error = 0
            if self.app.forest_graph.paths:
                for path in self.app.forest_graph.paths:
                    tid1, tid2 = path.tree1.tree_id, path.tree2.tree_id
                    x1, y1 = positions[tid1]
                    x2, y2 = positions[tid2]
                    
                    # 实际视觉距离
                    actual_dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    # 原始非归一化权重
                    desired_dist = path.weight
                    
                    # 计算比例误差
                    error = abs(actual_dist - desired_dist) / max(desired_dist, 0.1)
                    total_error += error
                
                avg_error = total_error / len(self.app.forest_graph.paths)
                print(f"布局平均误差率: {avg_error:.2f}")
            
            self.app.update_display()
            self.app.status_bar.set_text("✅ Data loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}", parent=self.root)

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
            self.add_path_mode = False
            self.delete_path_mode = False
            self.infection_sim_mode = False
            self.canvas.path_start = None
            self.delete_tree_mode = False
            self.canvas._shortest_path_highlight = []
            self.canvas._infection_highlight = set()
            self.canvas._infection_edge_highlight = set()
            self.canvas._infection_labels = {}
            # Reset all control panel buttons
            self.control_panel.add_path_btn.config(text="🔗 Add Path", command=self.start_add_path, style='Modern.TButton')
            self.control_panel.delete_path_btn.config(text="✂️ Delete Path", command=self.start_delete_path, style='Modern.TButton')
            self.control_panel.delete_tree_btn.config(text="🌳 Delete Tree", command=self.start_delete_tree, style='Modern.TButton')
            self.control_panel.infection_sim_btn.config(text="🦠 Infection Sim", command=self.enter_infection_sim_mode, style='Modern.TButton')
            self.app.status_bar.set_text("✅ Data cleared.")
            self.app.update_display()

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
            messagebox.showwarning("Warning", "Please click an INFECTED tree to start simulation.", parent=self.root)
            
    def _animate_infection(self, start_tree_id):
        """Animate BFS infection spread, highlight nodes and edges, mark infected nodes."""
        from ...algorithms.infection_simulation import simulate_infection
        import time
        infection_order = simulate_infection(self.app.forest_graph, start_tree_id)
        if not infection_order:
            self.app.status_bar.set_text("⚠️ Infection simulation failed.")
            return
        highlight_nodes = set()
        highlight_edges = set()
        for idx, (tid, from_id) in enumerate(infection_order):
            self.app.forest_graph.trees[tid].health_status = HealthStatus.INFECTED
            highlight_nodes.add(tid)
            if from_id is not None:
                highlight_edges.add((from_id, tid))
            # Canvas highlight: pass highlighted nodes and edges
            self.canvas._infection_highlight = set(highlight_nodes)
            self.canvas._infection_edge_highlight = set(highlight_edges)
            self.canvas._infection_labels = {tid: ("🦠" if idx==0 else "⚡") for tid, _ in infection_order[:idx+1]}
            self.app.update_display()
            self.app.root.update()
            time.sleep(0.3)
        self.app.status_bar.set_text(f"🦠 Infection simulation finished, infected trees: {len(infection_order)}")
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