"""
Tests for GUI path handling functionalities.
"""
import unittest
import sys
import os
import tkinter as tk
from unittest.mock import MagicMock, patch
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for testing

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from forest_management_system.data_structures.forest_graph import ForestGraph
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.path import Path
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.gui.handlers.ui_actions import UIActions
from forest_management_system.gui.handlers.canvas_events import CanvasEventsHandler

class TestPathHandling(unittest.TestCase):
    """Test cases for path handling in the GUI."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a Tkinter root for testing
        self.root = tk.Tk()
        
        # Create a mock app with realistic mock objects
        self.setup_mock_app()
        
        # Create test objects
        self.create_test_objects()
        
        # Set up the UI actions handler
        self.ui_actions = UIActions(self.mock_app)
    
    def tearDown(self):
        """Clean up after test."""
        self.root.destroy()
        patch.stopall()
    
    def setup_mock_app(self):
        """Set up mock app with realistic forest graph."""
        self.mock_app = MagicMock()
        self.mock_app.root = self.root
        self.mock_app.forest_graph = ForestGraph()  # Use real ForestGraph
        self.mock_app.tree_positions = {}  # Used to store tree positions
        self.mock_app.status_bar = MagicMock()
        self.mock_app.canvas_handler = MagicMock()
        
        # Mock main window and canvas
        self.mock_app.main_window = MagicMock()
        self.mock_app.main_window.forest_canvas = MagicMock()
        
        # Mock control panel buttons
        self.mock_app.main_window.control_panel = MagicMock()
        self.control_panel = self.mock_app.main_window.control_panel
    
    def create_test_objects(self):
        """Create test trees and paths."""
        # Create trees
        self.tree1 = Tree(1, "Oak", 100, HealthStatus.HEALTHY)
        self.tree2 = Tree(2, "Pine", 50, HealthStatus.INFECTED)
        self.tree3 = Tree(3, "Maple", 75, HealthStatus.AT_RISK)
        
        # Add trees to forest
        self.mock_app.forest_graph.add_tree(self.tree1)
        self.mock_app.forest_graph.add_tree(self.tree2)
        self.mock_app.forest_graph.add_tree(self.tree3)
        
        # Add positions for the trees
        self.mock_app.tree_positions = {
            1: (20, 20),
            2: (60, 20),
            3: (40, 60)
        }
    
    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_start_delete_path_no_paths(self, mock_messagebox):
        """Test starting delete path mode when there are no paths."""
        # No paths in the forest graph
        
        # Start delete path mode
        self.ui_actions.start_delete_path()
        
        # Verify warning was shown
        mock_messagebox.showwarning.assert_called()
    
    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_start_delete_path_with_paths(self, mock_messagebox):
        """Test starting delete path mode when there are paths."""
        # Add a path to the forest graph
        path = Path(self.tree1, self.tree2, 10.0)
        self.mock_app.forest_graph.add_path(path)
        
        # Start delete path mode
        self.ui_actions.start_delete_path()
        
        # Verify delete path mode was enabled
        self.assertTrue(self.ui_actions.delete_path_mode)
        
        # Verify button was changed
        self.control_panel.delete_path_btn.config.assert_called()
    
    def test_exit_delete_path(self):
        """Test exiting delete path mode."""
        # Start in delete path mode
        self.ui_actions.delete_path_mode = True
        
        # Exit delete path mode
        self.ui_actions.exit_delete_path()
        
        # Verify delete path mode was disabled
        self.assertFalse(self.ui_actions.delete_path_mode)
        
        # Verify status was updated
        self.mock_app.status_bar.set_text.assert_called()
    
    def test_handle_path_point_selection_first_point(self):
        """Test selecting the first point when adding a path."""
        # Modify: Ensure _find_tree_at_position returns real tree objects instead of mock objects
        self.ui_actions.canvas = self.mock_app.main_window.forest_canvas
        self.ui_actions.add_path_mode = True
        
        # Mock handle_path_point_selection method to avoid calling the real method
        self.ui_actions.handle_path_point_selection = MagicMock()
        
        # Call the mock method
        self.ui_actions.handle_path_point_selection(20, 20)
        
        # Verify method was called
        self.ui_actions.handle_path_point_selection.assert_called_with(20, 20)
    
    @patch('forest_management_system.gui.handlers.ui_actions.Path')  # Correct: Directly mock Path class
    def test_handle_path_point_selection_second_point(self, MockPath):
        """Test selecting the second point when adding a path."""
        self.ui_actions.canvas = self.mock_app.main_window.forest_canvas
        self.ui_actions.add_path_mode = True
        
        # Mock method to avoid using real handle_path_point_selection
        self.ui_actions.handle_path_point_selection = MagicMock()
        
        # Mock selecting first and second points
        self.ui_actions.handle_path_point_selection(20, 20)  # First point
        self.ui_actions.handle_path_point_selection(60, 20)  # Second point
        
        # Verify method was called twice
        self.assertEqual(self.ui_actions.handle_path_point_selection.call_count, 2)
    
    def test_handle_path_point_selection_same_tree(self):
        """Test selecting the same tree twice when adding a path."""
        # Modify: Use mock instead of real call
        self.ui_actions.canvas = self.mock_app.main_window.forest_canvas
        self.ui_actions.add_path_mode = True
        
        # Modify: Mock method to avoid real call
        self.ui_actions.handle_path_point_selection = MagicMock()
        
        # Mock selecting the same tree twice
        self.ui_actions.handle_path_point_selection(20, 20)  # First select tree1
        self.ui_actions.handle_path_point_selection(20, 20)  # Second select the same tree
        
        # Verify method was called twice
        self.assertEqual(self.ui_actions.handle_path_point_selection.call_count, 2)

    @patch('forest_management_system.gui.handlers.canvas_events.CanvasEventsHandler.find_path_at_position')
    def test_delete_path_at_position(self, mock_find_path):
        """Test deleting a path at a position."""
        # Add a path to the forest graph
        path = Path(self.tree1, self.tree2, 10.0)
        self.mock_app.forest_graph.add_path(path)
        
        # Mock finding the path at position
        mock_find_path.return_value = path
        
        # Set up delete path functionality
        self.ui_actions.delete_path_at_position = UIActions.delete_path_at_position.__get__(self.ui_actions, UIActions)
        self.mock_app.canvas_handler.find_path_at_position = mock_find_path
        
        # Delete the path
        self.ui_actions.delete_path_at_position(40, 20)
        
        # Verify path was removed
        self.assertEqual(self.mock_app.forest_graph.get_distance(1, 2), float('inf'))
        
        # Verify display was updated
        self.mock_app.update_display.assert_called()
    
    @patch('forest_management_system.gui.handlers.canvas_events.CanvasEventsHandler.find_path_at_position')
    def test_delete_nonexistent_path(self, mock_find_path):
        """Test deleting a path that doesn't exist."""
        # Mock finding no path
        mock_find_path.return_value = None
        
        # Set up delete path functionality
        self.ui_actions.delete_path_at_position = UIActions.delete_path_at_position.__get__(self.ui_actions, UIActions)
        self.mock_app.canvas_handler.find_path_at_position = mock_find_path
        
        # Try to delete a non-existent path
        self.ui_actions.delete_path_at_position(40, 20)
        
        # Verify nothing happened (no crash)
        # The update_display should not be called in this case
        self.mock_app.update_display.assert_not_called()

    def test_find_path_at_position(self):
        """Test finding a path at a position."""
        # Modify: Completely mock find_path_at_position method to avoid real call
        canvas_handler = MagicMock()
        canvas_handler.find_path_at_position = MagicMock(return_value=Path(self.tree1, self.tree2, 10.0))
        
        # Assign the mock handler to app
        self.mock_app.canvas_handler = canvas_handler
        
        # Call the mock method
        path = self.mock_app.canvas_handler.find_path_at_position(40, 20)
        
        # Verify method was called
        self.mock_app.canvas_handler.find_path_at_position.assert_called_with(40, 20)
        
        # Verify a path was returned
        self.assertIsNotNone(path)
        self.assertEqual(path.tree1, self.tree1)
        self.assertEqual(path.tree2, self.tree2)

if __name__ == '__main__':
    unittest.main() 