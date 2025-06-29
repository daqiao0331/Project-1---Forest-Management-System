"""
Main entry point for the Forest Management System GUI.
"""
import sys
import os
import tkinter as tk

# Set the correct path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from forest_management_system.gui.app import AppLogic

def main():
    root = tk.Tk()
    app = AppLogic(root)
    app.run()

if __name__ == "__main__":
    main()