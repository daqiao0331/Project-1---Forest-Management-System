import unittest
from unittest.mock import MagicMock, patch

# Import the MainWindow class
from forest_management_system.gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    """
    Unit tests for the MainWindow class.
    """
    def setUp(self):
        # Patch tkinter and all panel dependencies
        patcher_tk = patch('forest_management_system.gui.main_window.tk')
        patcher_ttk = patch('forest_management_system.gui.main_window.ttk')
        patcher_control_panel = patch('forest_management_system.gui.main_window.ControlPanel')
        patcher_forest_canvas = patch('forest_management_system.gui.main_window.ForestCanvas')
        patcher_info_panel = patch('forest_management_system.gui.main_window.InfoPanel')
        patcher_status_bar = patch('forest_management_system.gui.main_window.StatusBar')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.mock_control_panel = patcher_control_panel.start()
        self.mock_forest_canvas = patcher_forest_canvas.start()
        self.mock_info_panel = patcher_info_panel.start()
        self.mock_status_bar = patcher_status_bar.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.addCleanup(patcher_control_panel.stop)
        self.addCleanup(patcher_forest_canvas.stop)
        self.addCleanup(patcher_info_panel.stop)
        self.addCleanup(patcher_status_bar.stop)
        self.root = MagicMock()

    def test_init(self):
        """
        Test that MainWindow initializes all components and sets up the layout.
        """
        window = MainWindow(self.root)
        self.assertIsNotNone(window.control_panel)
        self.assertIsNotNone(window.forest_canvas)
        self.assertIsNotNone(window.info_panel)
        self.assertIsNotNone(window.status_bar)
        self.root.title.assert_called_once()
        self.root.geometry.assert_called_once()
        self.root.configure.assert_called_once()
        self.root.state.assert_called_once()

    def test_configure_styles(self):
        """
        Test that _configure_styles sets up ttk styles.
        """
        window = MainWindow(self.root)
        # Should call ttk.Style and configure styles
        self.assertTrue(self.mock_ttk.Style.called)

    def test_setup_title_bar(self):
        """
        Test that _setup_title_bar creates a title bar frame and label.
        """
        window = MainWindow(self.root)
        parent = MagicMock()
        window._setup_title_bar(parent)
        # Should create a Frame and a Label
        self.assertTrue(self.mock_tk.Frame.called)
        self.assertTrue(self.mock_tk.Label.called)

if __name__ == '__main__':
    unittest.main() 