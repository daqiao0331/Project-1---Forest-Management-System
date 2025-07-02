import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.handlers.canvas_events import CanvasEventsHandler
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus

class TestCanvasEventsHandler(unittest.TestCase):
    """
    Unit tests for the CanvasEventsHandler class.
    """
    def setUp(self):
        self.app = MagicMock()
        self.app.main_window.forest_canvas = MagicMock()
        self.app.ui_actions = MagicMock()
        self.app.status_bar = MagicMock()
        self.app.tree_positions = {1: (10, 10)}
        self.app.forest_graph = MagicMock()
        self.app.forest_graph.trees = {1: MagicMock(tree_id=1, species='Pine', age=10, health_status=MagicMock(name='HEALTHY'))}
        self.app.forest_graph.adj_list = {1: {2: 5.0}, 2: {1: 5.0}}
        self.handler = CanvasEventsHandler(self.app)
        self.handler.canvas = self.app.main_window.forest_canvas
        # 创建共享mock对象用于测试
        self.mock_ax = MagicMock()
        self.handler.canvas.ax = self.mock_ax

    def test_on_press_select_tree(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 10, 10
        self.app.ui_actions.delete_tree_mode = False
        self.app.ui_actions.delete_path_mode = False
        self.app.ui_actions.infection_sim_mode = False
        self.app.ui_actions.add_path_mode = False
        self.handler._find_tree_at_position = MagicMock(return_value=self.app.forest_graph.trees[1])
        self.handler.on_press(event)
        self.assertTrue(self.handler.dragging)
        self.assertEqual(self.handler.drag_tree, self.app.forest_graph.trees[1])
        self.app.status_bar.set_text.assert_called()
        self.app.update_display.assert_called()

    def test_on_press_no_tree(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 100, 100
        self.app.ui_actions.delete_tree_mode = False
        self.app.ui_actions.delete_path_mode = False
        self.app.ui_actions.infection_sim_mode = False
        self.app.ui_actions.add_path_mode = False
        self.handler._find_tree_at_position = MagicMock(return_value=None)
        self.handler.on_press(event)
        self.assertFalse(self.handler.dragging)
        self.app.status_bar.set_text.assert_called_with("Ready")
        self.app.update_display.assert_called()

    def test_on_press_delete_tree_mode(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 10, 10
        self.app.ui_actions.delete_tree_mode = True
        self.handler.on_press(event)
        self.app.ui_actions.delete_tree_at_position.assert_called_with(10, 10)

    def test_on_press_delete_path_mode(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 10, 10
        self.app.ui_actions.delete_tree_mode = False
        self.app.ui_actions.delete_path_mode = True
        self.handler.on_press(event)
        self.app.ui_actions.delete_path_at_position.assert_called_with(10, 10)

    def test_on_press_infection_sim_mode(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 10, 10
        self.app.ui_actions.delete_tree_mode = False
        self.app.ui_actions.delete_path_mode = False
        self.app.ui_actions.infection_sim_mode = True
        self.handler.on_press(event)
        self.app.ui_actions.start_infection_at_position.assert_called_with(10, 10)

    def test_on_press_add_path_mode(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.xdata, event.ydata = 10, 10
        self.app.ui_actions.delete_tree_mode = False
        self.app.ui_actions.delete_path_mode = False
        self.app.ui_actions.infection_sim_mode = False
        self.app.ui_actions.add_path_mode = True
        self.handler.on_press(event)
        self.app.ui_actions.handle_path_point_selection.assert_called_with(10, 10)

    def test_on_press_outside_axes(self):
        event = MagicMock()
        event.inaxes = None  
        self.handler.on_press(event)
        self.app.status_bar.set_text.assert_not_called()
        self.app.update_display.assert_not_called()

    def test_on_motion_dragging(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.button = 1
        event.xdata, event.ydata = 20, 20
        self.handler.dragging = True
        self.handler.drag_tree = MagicMock(tree_id=1)
        self.app.forest_graph.adj_list = {1: {2: 5.0}, 2: {1: 5.0}}
        self.app.tree_positions = {1: (10, 10), 2: (20, 20)}
        self.app.forest_graph.update_distance = MagicMock()
        self.handler.on_motion(event)
        self.app.forest_graph.update_distance.assert_called()
        self.app.update_display.assert_called()
        self.app.status_bar.set_text.assert_called()

    def test_on_motion_hover_tree(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.button = None
        event.xdata, event.ydata = 10, 10
        self.handler.dragging = False
        self.handler._find_tree_at_position = MagicMock(return_value=self.app.forest_graph.trees[1])
        self.handler.canvas.show_tooltip = MagicMock()
        self.handler.on_motion(event)
        self.handler.canvas.show_tooltip.assert_called()

    def test_on_motion_no_tree(self):
        event = MagicMock()
        event.inaxes = self.mock_ax
        event.button = None
        event.xdata, event.ydata = 100, 100
        self.handler.dragging = False
        self.handler._find_tree_at_position = MagicMock(return_value=None)
        self.handler.canvas.hide_tooltip = MagicMock()
        self.handler.on_motion(event)
        self.handler.canvas.hide_tooltip.assert_called()

    def test_on_motion_outside_axes(self):
        event = MagicMock()
        event.inaxes = None  # 不是canvas.ax
        self.handler.canvas.hide_tooltip = MagicMock()
        self.handler.on_motion(event)
        self.handler.canvas.hide_tooltip.assert_called()

    def test_on_release(self):
        event = MagicMock()
        self.handler.dragging = True
        self.handler.drag_tree = MagicMock(tree_id=1)
        self.handler.on_release(event)
        self.assertFalse(self.handler.dragging)
        self.app.status_bar.set_text.assert_called()
        self.app.update_display.assert_called()

    def test_on_release_not_dragging(self):
        event = MagicMock()
        self.handler.dragging = False
        self.handler.drag_tree = None
        self.handler.on_release(event)
        self.assertFalse(self.handler.dragging)
        self.app.status_bar.set_text.assert_not_called()
        self.app.update_display.assert_not_called()

    def test_find_tree_at_position_none(self):
        result = self.handler._find_tree_at_position(None, None)
        self.assertIsNone(result)

    def test_find_tree_at_position_found(self):
        self.app.tree_positions = {1: (10, 10)}
        self.app.forest_graph.trees = {1: MagicMock(tree_id=1)}
        result = self.handler._find_tree_at_position(10, 10)
        self.assertIsNotNone(result)

    def test_find_tree_at_position_not_found(self):
        self.app.tree_positions = {1: (10, 10)}
        self.app.forest_graph.trees = {1: MagicMock(tree_id=1)}
        result = self.handler._find_tree_at_position(100, 100)
        self.assertIsNone(result)

    def test_find_path_at_position_none(self):
        result = self.handler.find_path_at_position(None, None)
        self.assertIsNone(result)

    def test_find_path_at_position_found(self):
        tree1 = Tree(1, "Pine", 10, HealthStatus.HEALTHY)
        tree2 = Tree(2, "Oak", 15, HealthStatus.HEALTHY)
        
        self.app.forest_graph.adj_list = {1: {2: 1.0}, 2: {1: 1.0}}
        self.app.tree_positions = {1: (0, 0), 2: (0, 0)}
        self.app.forest_graph.trees = {1: tree1, 2: tree2}
        
        with patch('forest_management_system.gui.handlers.canvas_events.Path') as MockPath:
            MockPath.return_value = MagicMock()
            result = self.handler.find_path_at_position(0, 0)
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main() 