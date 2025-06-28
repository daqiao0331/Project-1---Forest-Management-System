"""
Tests for the GUI action handlers.
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

# Mocking modules that are not easily available in a test environment
# or need to be faked.
sys_modules_mock = {
    'forest_management_system.gui.main_window': MagicMock(),
    'forest_management_system.gui.handlers.canvas_events': MagicMock(),
    'forest_management_system.components.forest_graph': MagicMock(),
    'forest_management_system.algorithms.reserve_detection': MagicMock(),
    'forest_management_system.gui.dialogs.tree_dialogs': MagicMock(),
    'forest_management_system.components.tree': MagicMock(),
}

with patch.dict('sys.modules', sys_modules_mock):
    from forest_management_system.gui.handlers.ui_actions import UIActions
    from forest_management_system.gui.app import AppLogic

class TestUIActions(unittest.TestCase):

    def setUp(self):
        """Set up a mock application environment before each test."""
        # Create a mock for the main AppLogic
        self.mock_app = MagicMock(spec=AppLogic)
        
        # Tkinter root is needed for some dialogs, so we create a real one
        self.root = tk.Tk()
        self.mock_app.root = self.root
        
        # Mock other parts of the app
        self.mock_app.forest_graph = MagicMock()
        self.mock_app.tree_positions = {}
        self.mock_app.main_window = MagicMock()
        self.mock_app.status_bar = MagicMock()
        
        # Instance of the class we are testing
        self.ui_actions = UIActions(self.mock_app)

    def tearDown(self):
        """Destroy the Tkinter root window after each test."""
        self.root.destroy()

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    def test_add_tree_successful(self, MockAddTreeDialog):
        """Test if a tree is added correctly when the dialog returns valid data."""
        # Arrange: Configure the mock dialog to return a successful result
        mock_dialog_instance = MockAddTreeDialog.return_value
        mock_dialog_instance.show.return_value = {
            "species": "Oak",
            "age": 50,
            "health": "HEALTHY" # Assuming the dialog returns a string
        }
        self.mock_app.forest_graph.trees.values.return_value = []

        # Act: Call the method to test
        self.ui_actions.add_tree()

        # Assert: Check if the application state was updated as expected
        self.mock_app.forest_graph.add_tree.assert_called_once()
        self.assertEqual(len(self.mock_app.tree_positions), 1)
        self.mock_app.update_display.assert_called_once()
        self.mock_app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    def test_add_tree_cancelled(self, MockAddTreeDialog):
        """Test that nothing happens if the add tree dialog is cancelled."""
        # Arrange: Configure the mock dialog to simulate cancellation
        mock_dialog_instance = MockAddTreeDialog.return_value
        mock_dialog_instance.show.return_value = None

        # Act: Call the method
        self.ui_actions.add_tree()

        # Assert: Ensure no changes were made
        self.mock_app.forest_graph.add_tree.assert_not_called()
        self.mock_app.update_display.assert_not_called()

    def test_clear_data_confirmed(self):
        """Test if data is cleared after user confirmation."""
        # Arrange
        with patch('tkinter.messagebox.askyesno', return_value=True):
            # Act
            self.ui_actions.clear_data()
            # Assert
            self.mock_app.forest_graph.clear.assert_called_once()
            self.assertTrue(not self.mock_app.tree_positions) # Check if dict is empty
            self.mock_app.update_display.assert_called_once()
    
    def test_clear_data_cancelled(self):
        """Test that data is not cleared if the user cancels."""
        # Arrange
        with patch('tkinter.messagebox.askyesno', return_value=False):
            # Act
            self.ui_actions.clear_data()
            # Assert
            self.mock_app.forest_graph.clear.assert_not_called()

if __name__ == '__main__':
    unittest.main() 