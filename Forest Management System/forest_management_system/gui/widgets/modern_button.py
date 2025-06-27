"""
Custom, modern-styled widgets for the application.
"""
from tkinter import ttk
 
class ModernButton(ttk.Button):
    """A custom ttk.Button with a modern style."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Modern.TButton', **kwargs) 