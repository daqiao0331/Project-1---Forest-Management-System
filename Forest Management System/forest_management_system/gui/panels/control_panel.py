"""
The control panel containing all the action buttons.
"""
import tkinter as tk
from tkinter import ttk
from ..widgets.modern_button import ModernButton

class ControlPanel:
    """Manages the control panel with all its buttons."""
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#ffffff', width=420)
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.frame.pack_propagate(False)
        
        # Setup scrollable frame
        sidebar_canvas = tk.Canvas(self.frame, bg='#ffffff', highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=sidebar_canvas.yview)
        self.scrollable_frame = tk.Frame(sidebar_canvas, bg='#ffffff')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
        )
        
        sidebar_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Create a frame for dynamic action buttons
        self.actions_frame = ttk.LabelFrame(self.scrollable_frame, text="🔄 Dynamic Actions", 
                                   style='Modern.TLabelframe', padding=15)
        
        self._create_button_sections()

    def _create_button_sections(self):
        """Create sections for different types of operations."""
        # Tree Operations
        tree_frame = ttk.LabelFrame(self.scrollable_frame, text="🌳 Tree Operations", 
                                   style='Modern.TLabelframe', padding=15)
        tree_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        self.add_tree_btn = ModernButton(tree_frame, text="➕  Add Tree")
        self.add_tree_btn.pack(fill=tk.X, pady=3)
        self.delete_tree_btn = ModernButton(tree_frame, text="✖  Delete Tree")
        self.delete_tree_btn.pack(fill=tk.X, pady=3)
        self.modify_health_btn = ModernButton(tree_frame, text="🔧  Modify Health")
        self.modify_health_btn.pack(fill=tk.X, pady=3)

        # Path Operations
        path_frame = ttk.LabelFrame(self.scrollable_frame, text="🛤️ Path Operations", 
                                   style='Modern.TLabelframe', padding=15)
        path_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        self.add_path_btn = ModernButton(path_frame, text="🔗  Add Path")
        self.add_path_btn.pack(fill=tk.X, pady=3)
        self.delete_path_btn = ModernButton(path_frame, text="✂️  Delete Path")
        self.delete_path_btn.pack(fill=tk.X, pady=3)
        self.shortest_path_btn = ModernButton(path_frame, text="🔵  Shortest Path")
        self.shortest_path_btn.pack(fill=tk.X, pady=3)

        # Data Operations
        data_frame = ttk.LabelFrame(self.scrollable_frame, text="💾 Data Operations", 
                                   style='Modern.TLabelframe', padding=15)
        data_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        self.load_data_btn = ModernButton(data_frame, text="📂  Load Data")
        self.load_data_btn.pack(fill=tk.X, pady=3)
        self.save_data_btn = ModernButton(data_frame, text="💾  Save Data")
        self.save_data_btn.pack(fill=tk.X, pady=3)
        self.restore_original_btn = ttk.Button(data_frame, text="🔄  Restore Original Data", style='Blue.TButton')
        self.restore_original_btn.pack(fill=tk.X, pady=3)
        self.restore_original_btn.config(state=tk.DISABLED)  # Initially disabled
        self.clear_data_btn = ModernButton(data_frame, text="✖  Clear Data")
        self.clear_data_btn.pack(fill=tk.X, pady=3)
        self.infection_sim_btn = ModernButton(data_frame, text="🦠  Infection Sim")
        self.infection_sim_btn.pack(fill=tk.X, pady=3)
        self.analyze_forest_btn = ModernButton(data_frame, text="📊  Analyze Forest")
        self.analyze_forest_btn.pack(fill=tk.X, pady=3)
        
        # Pack the dynamic actions frame last so it appears at the bottom
        self.actions_frame.pack(fill=tk.X, pady=(0, 15), padx=5)

    def connect_actions(self, actions):
        """Connect button commands to the UI actions handler."""
        self.add_tree_btn.config(command=actions.add_tree)
        self.delete_tree_btn.config(command=actions.start_delete_tree)
        self.modify_health_btn.config(command=actions.modify_health)
        
        self.add_path_btn.config(command=actions.start_add_path)
        self.delete_path_btn.config(command=actions.start_delete_path)
        self.shortest_path_btn.config(command=actions.find_shortest_path)

        self.load_data_btn.config(command=actions.load_data)
        self.save_data_btn.config(command=actions.save_data)
        self.restore_original_btn.config(command=actions.restore_original_data)
        self.clear_data_btn.config(command=actions.clear_data)
        self.infection_sim_btn.config(command=actions.enter_infection_sim_mode)
        self.analyze_forest_btn.config(command=actions.analyze_forest)