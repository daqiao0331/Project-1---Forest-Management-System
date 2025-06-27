"""
The status bar widget for the main application window.
"""
import tkinter as tk

class StatusBar:
    """Manages the application's status bar."""
    def __init__(self, parent):
        self.label = tk.Label(parent, text="Ready", 
                             relief=tk.SUNKEN, anchor=tk.W,
                             font=('Segoe UI', 9),
                             bg='#ecf0f1', fg='#2c3e50')
        self.label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def set_text(self, text):
        """Updates the text displayed in the status bar."""
        self.label.config(text=text) 