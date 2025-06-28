"""
Tests for the GUI action handlers.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import sys
import os

# Add the parent directory to the Python path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import UIActions directly - we'll mock its dependencies
from forest_management_system.gui.handlers.ui_actions import UIActions
from forest_management_system.components.health_status import HealthStatus
from forest_management_system.components.tree import Tree

class TestUIActions(unittest.TestCase):

    def setUp(self):
        """Set up a clean test environment before each test."""
        # Create a real Tkinter root for dialog tests
        self.root = tk.Tk()
        
        # Create a clean mock app with only what we need
        self.mock_app = MagicMock()
        self.mock_app.root = self.root
        self.mock_app.forest_graph = MagicMock()
        self.mock_app.tree_positions = {}
        self.mock_app.main_window = MagicMock()
        self.mock_app.status_bar = MagicMock()
        
        # Create the UIActions instance with our controlled mock app
        self.ui_actions = UIActions(self.mock_app)

    def tearDown(self):
        """Clean up after each test."""
        self.root.destroy()
        # Ensure all patches are stopped
        patch.stopall()

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    def test_add_tree_successful(self, MockAddTreeDialog):
        """Test if a tree is added correctly when the dialog returns valid data."""
        # Configure mock to return success
        mock_dialog = MagicMock()
        MockAddTreeDialog.return_value = mock_dialog
        mock_dialog.show.return_value = {
            "species": "Oak",
            "age": 50,
            "health": HealthStatus.HEALTHY  # Use actual enum value
        }
        
        # Reset the mock to ensure clean state
        self.mock_app.forest_graph.add_tree.reset_mock()
        
        # Execute the method
        self.ui_actions.add_tree()
        
        # Verify the tree was added
        self.mock_app.forest_graph.add_tree.assert_called_once()
        self.mock_app.update_display.assert_called_once()

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    def test_add_tree_cancelled(self, MockAddTreeDialog):
        """Test that nothing happens if the add tree dialog is cancelled."""
        # Configure mock to return None (cancelled)
        mock_dialog = MagicMock()
        MockAddTreeDialog.return_value = mock_dialog
        mock_dialog.show.return_value = None
        
        # Reset the mock to ensure clean state
        self.mock_app.forest_graph.add_tree.reset_mock()
        self.mock_app.update_display.reset_mock()
        
        # Execute the method
        self.ui_actions.add_tree()
        
        # Verify nothing happened
        self.mock_app.forest_graph.add_tree.assert_not_called()
        self.mock_app.update_display.assert_not_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox.askyesno')
    def test_clear_data_confirmed(self, mock_askyesno):
        """Test if data is cleared after user confirmation."""
        # Configure mock to return True (confirmed)
        mock_askyesno.return_value = True
        
        # Reset mocks
        self.mock_app.forest_graph.clear.reset_mock()
        self.mock_app.update_display.reset_mock()
        
        # Execute the method
        self.ui_actions.clear_data()
        
        # Verify data was cleared
        self.mock_app.forest_graph.clear.assert_called_once()
        self.assertTrue(not self.mock_app.tree_positions)  # Check if dict is empty
        self.mock_app.update_display.assert_called_once()
    
    @patch('forest_management_system.gui.handlers.ui_actions.messagebox.askyesno')
    def test_clear_data_cancelled(self, mock_askyesno):
        """Test that data is not cleared if the user cancels."""
        # Configure mock to return False (cancelled)
        mock_askyesno.return_value = False
        
        # Reset mock
        self.mock_app.forest_graph.clear.reset_mock()
        
        # Execute the method
        self.ui_actions.clear_data()
        
        # Verify nothing happened
        self.mock_app.forest_graph.clear.assert_not_called()

if __name__ == '__main__':
    unittest.main() 