import unittest
from unittest.mock import MagicMock, patch

from forest_management_system.gui.app import AppLogic

class TestAppLogic(unittest.TestCase):
    """
    Unit tests for the AppLogic class.
    """
    def setUp(self):
        # Patch tkinter, MainWindow, UIActions, CanvasEventsHandler, and all external dependencies
        patcher_tk = patch('forest_management_system.gui.app.tk')
        patcher_main_window = patch('forest_management_system.gui.app.MainWindow')
        patcher_ui_actions = patch('forest_management_system.gui.app.UIActions')
        patcher_canvas_handler = patch('forest_management_system.gui.app.CanvasEventsHandler')
        patcher_forest_graph = patch('forest_management_system.gui.app.ForestGraph')
        patcher_find_reserves = patch('forest_management_system.gui.app.find_reserves')
        patcher_copy = patch('forest_management_system.gui.app.copy')
        self.mock_tk = patcher_tk.start()
        self.mock_main_window = patcher_main_window.start()
        self.mock_ui_actions = patcher_ui_actions.start()
        self.mock_canvas_handler = patcher_canvas_handler.start()
        self.mock_forest_graph = patcher_forest_graph.start()
        self.mock_find_reserves = patcher_find_reserves.start()
        self.mock_copy = patcher_copy.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_main_window.stop)
        self.addCleanup(patcher_ui_actions.stop)
        self.addCleanup(patcher_canvas_handler.stop)
        self.addCleanup(patcher_forest_graph.stop)
        self.addCleanup(patcher_find_reserves.stop)
        self.addCleanup(patcher_copy.stop)
        self.root = MagicMock()

    def test_init(self):
        """
        Test that AppLogic initializes all components and sets up handlers and connections.
        """
        app = AppLogic(self.root)
        self.assertIsNotNone(app.main_window)
        self.assertIsNotNone(app.ui_actions)
        self.assertIsNotNone(app.canvas_handler)
        self.assertIsNotNone(app.forest_graph)
        self.assertIsNotNone(app.tree_positions)
        self.assertIsNotNone(app.status_bar)

    def test_update_display(self):
        """
        Test that update_display calls draw_forest and update_info.
        """
        app = AppLogic(self.root)
        app.main_window.forest_canvas = MagicMock()
        app.main_window.info_panel = MagicMock()
        app.forest_graph = MagicMock()
        app.tree_positions = MagicMock()
        app.update_display()
        app.main_window.forest_canvas.draw_forest.assert_called_once()
        app.main_window.info_panel.update_info.assert_called_once()

    def test_create_snapshot(self):
        """
        Test that create_snapshot stores deep copies of forest_graph and tree_positions.
        """
        app = AppLogic(self.root)
        app.forest_graph = MagicMock()
        app.tree_positions = MagicMock()
        app.create_snapshot()
        self.assertTrue(app.has_snapshot)
        self.mock_copy.deepcopy.assert_any_call(app.forest_graph)
        self.mock_copy.deepcopy.assert_any_call(app.tree_positions)

    def test_restore_snapshot_success(self):
        """
        Test that restore_snapshot restores data and updates display when snapshot exists.
        """
        app = AppLogic(self.root)
        app.has_snapshot = True
        app.snapshot_forest_graph = MagicMock()
        app.snapshot_tree_positions = MagicMock()
        app.update_display = MagicMock()
        self.mock_copy.deepcopy.side_effect = lambda x: x
        result = app.restore_snapshot()
        self.assertTrue(result)
        app.update_display.assert_called_once()

    def test_restore_snapshot_fail(self):
        """
        Test that restore_snapshot returns False when no snapshot exists.
        """
        app = AppLogic(self.root)
        app.has_snapshot = False
        result = app.restore_snapshot()
        self.assertFalse(result)

    def test_run(self):
        """
        Test that run calls root.mainloop().
        """
        app = AppLogic(self.root)
        app.root = MagicMock()
        app.run()
        app.root.mainloop.assert_called_once()

if __name__ == '__main__':
    unittest.main() 