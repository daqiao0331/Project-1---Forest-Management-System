"""
Defines the main window structure and layout of the application.
"""
import tkinter as tk
from tkinter import ttk
from .panels.control_panel import ControlPanel
from .panels.forest_canvas import ForestCanvas
from .panels.info_panel import InfoPanel
from .panels.status_bar import StatusBar

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🌲 Forest Management System")
        self.root.geometry("1600x1000")  # Restore original window size
        self.root.configure(bg='#f0f0f0')
        self.root.state('zoomed')

        self._configure_styles()
        
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)  # Restore original margins
        
        self._setup_title_bar(main_container)
        
        content_frame = tk.Frame(main_container, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)

        self.control_panel = ControlPanel(content_frame)
        self.forest_canvas = ForestCanvas(content_frame)
        self.info_panel = InfoPanel(self.control_panel.scrollable_frame)
        self.status_bar = StatusBar(main_container)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TButton', padding=(18, 10), font=('Segoe UI', 15, 'bold'),
                        background='#4CAF50', foreground='white')
        style.map('Modern.TButton', background=[('active', '#45a049')])
        style.configure('Red.TButton', background='#e74c3c', foreground='white', 
                        font=('Segoe UI', 15, 'bold'), padding=(18, 10))
        style.map('Red.TButton', background=[('active', '#c0392b')])
        style.configure('Modern.TLabelframe', background='#ffffff', relief='flat', borderwidth=1)
        style.configure('Modern.TLabelframe.Label', font=('Segoe UI', 16, 'bold'), 
                        foreground='#2c3e50', background='#ffffff')

    def _setup_title_bar(self, parent):
        title_frame = tk.Frame(parent, bg='#2c3e50', height=60)  # Restore original height
        title_frame.pack(fill=tk.X, pady=(0, 15))  # Restore original margins
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="🌲 Forest Management System", 
                 font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50').pack(expand=True) 