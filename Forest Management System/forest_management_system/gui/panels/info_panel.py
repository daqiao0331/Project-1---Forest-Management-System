"""
The information panel for displaying forest statistics.
"""
import tkinter as tk
from tkinter import ttk
from collections import Counter

class InfoPanel:
    """Displays statistics about the forest."""
    def __init__(self, parent_frame):
        info_frame = ttk.LabelFrame(parent_frame, text="📊 Forest Information", 
                                   style='Modern.TLabelframe', padding=15)
        info_frame.pack(fill=tk.X)
        
        info_text_frame = tk.Frame(info_frame, bg='#ffffff')
        info_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_text_frame, height=22, width=35, 
                                font=('Consolas', 13),
                                bg='#f8f9fa', fg='#2c3e50',
                                relief='flat', borderwidth=1,
                                padx=10, pady=10)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.info_text.bind('<Enter>', self._bind_mouse_wheel)
        self.info_text.bind('<Leave>', self._unbind_mouse_wheel)

    def _bind_mouse_wheel(self, event):
        self.info_text.bind_all('<MouseWheel>', self._on_mouse_wheel)

    def _unbind_mouse_wheel(self, event):
        self.info_text.unbind_all('<MouseWheel>')

    def _on_mouse_wheel(self, event):
        self.info_text.yview_scroll(int(-1*(event.delta/120)), 'units')

    def update_info(self, forest_graph, find_reserves_func):
        """Updates the text area with the latest forest statistics."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        tree_count = len(forest_graph.trees)
        path_count = len(forest_graph.paths)
        
        try:
            reserves = find_reserves_func(forest_graph)
            reserve_count = len(reserves)
            max_reserve = max((len(r) for r in reserves), default=0)
        except Exception:
            reserve_count = 0
            max_reserve = 0
            
        infected_count = sum(1 for t in forest_graph.trees.values() if t.health_status.name == "INFECTED")
        infected_percent = (infected_count / tree_count * 100) if tree_count else 0
        
        info = f"🌲 FOREST STATISTICS\n"
        info += "="*30 + "\n"
        info += f"📊 Tree Count: {tree_count}\n"
        info += f"🛤️ Path Count: {path_count}\n"
        info += f"🏕️ Reserve Count: {reserve_count}\n"
        info += f"🏞️ Max Reserve Size: {max_reserve}\n"
        info += f"🔴 Infected %: {infected_percent:.1f}%\n\n"
        
        health_stats = Counter(t.health_status.name for t in forest_graph.trees.values())
        info += f"🏥 HEALTH STATUS\n"
        info += "="*30 + "\n"
        for status, count in health_stats.items():
            emoji = "🟢" if status == "HEALTHY" else "🔴" if status == "INFECTED" else "🟠"
            info += f"{emoji} {status}: {count}\n"
            
        species_stats = Counter(t.species for t in forest_graph.trees.values())
        info += f"\n🌳 SPECIES DISTRIBUTION\n"
        info += "="*30 + "\n"
        for species, count in species_stats.items():
            info += f"🌲 {species}: {count}\n"
            
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)