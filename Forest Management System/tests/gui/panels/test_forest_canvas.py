import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.panels.forest_canvas import ForestCanvas

class TestForestCanvas(unittest.TestCase):
    """
    Unit tests for the ForestCanvas class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.panels.forest_canvas.tk')
        patcher_plt = patch('forest_management_system.gui.panels.forest_canvas.plt')
        patcher_FigureCanvasTkAgg = patch('forest_management_system.gui.panels.forest_canvas.FigureCanvasTkAgg')
        patcher_Circle = patch('forest_management_system.gui.panels.forest_canvas.Circle')
        patcher_Rectangle = patch('forest_management_system.gui.panels.forest_canvas.Rectangle')
        patcher_np = patch('forest_management_system.gui.panels.forest_canvas.np')
        self.mock_tk = patcher_tk.start()
        self.mock_plt = patcher_plt.start()
        self.mock_FigureCanvasTkAgg = patcher_FigureCanvasTkAgg.start()
        self.mock_Circle = patcher_Circle.start()
        self.mock_Rectangle = patcher_Rectangle.start()
        self.mock_np = patcher_np.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_plt.stop)
        self.addCleanup(patcher_FigureCanvasTkAgg.stop)
        self.addCleanup(patcher_Circle.stop)
        self.addCleanup(patcher_Rectangle.stop)
        self.addCleanup(patcher_np.stop)
        self.parent = MagicMock()
        self.canvas = ForestCanvas(self.parent)

    def test_setup_canvas_bindings(self):
        handler = MagicMock()
        self.canvas.canvas.mpl_connect = MagicMock()
        self.canvas.setup_canvas_bindings(handler)
        self.assertTrue(self.canvas.canvas.mpl_connect.called)

    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_draw_forest(self, mock_find_reserves):
        mock_find_reserves.return_value = []
        forest_graph = MagicMock()
        forest_graph.adj_list = {}
        forest_graph.trees = {}
        tree_positions = {}
        self.canvas.ax = MagicMock()
        self.canvas.draw_forest(forest_graph, tree_positions)
        self.canvas.ax.clear.assert_called()
        self.canvas.ax.set_xlim.assert_called()
        self.canvas.ax.set_ylim.assert_called()
        self.canvas.ax.set_aspect.assert_called()
        self.canvas.ax.grid.assert_called()
        self.canvas.ax.set_facecolor.assert_called()

    def test_show_tooltip(self):
        self.canvas._tooltip = None
        self.canvas.canvas = MagicMock()
        self.canvas.ax = MagicMock()
        self.canvas.show_tooltip(10, 10, "Test")
        self.assertIsNotNone(self.canvas._tooltip)

    def test_hide_tooltip(self):
        self.canvas._tooltip = MagicMock()
        self.canvas.hide_tooltip()
        self.assertIsNone(self.canvas._tooltip)

    def test_get_emoji_font(self):
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Segoe UI Emoji'), MagicMock(name='Other Font')]):
            font = self.canvas._get_emoji_font()
            self.assertIn(font, ['Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans'])

    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_draw_forest_with_paths_and_trees(self, mock_find_reserves):
        mock_find_reserves.return_value = [[1,2]]
        forest_graph = MagicMock()
        forest_graph.adj_list = {1: {2: 1.0}, 2: {1: 1.0}}
        forest_graph.trees = {1: MagicMock(tree_id=1, health_status=MagicMock(name='HEALTHY')), 2: MagicMock(tree_id=2, health_status=MagicMock(name='INFECTED'))}
        tree_positions = {1: (10, 10), 2: (20, 20)}
        self.canvas.ax = MagicMock()
        self.canvas._shortest_path_highlight = [1, 2]
        self.canvas.draw_forest(forest_graph, tree_positions)
        self.canvas.ax.clear.assert_called()
        self.canvas.ax.set_xlim.assert_called()
        self.canvas.ax.set_ylim.assert_called()
        self.canvas.ax.set_aspect.assert_called()
        self.canvas.ax.grid.assert_called()
        self.canvas.ax.set_facecolor.assert_called()

    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_draw_forest_with_reserves_and_selection(self, mock_find_reserves):
        # Test reserves drawing and selection circle
        mock_find_reserves.return_value = [[1, 2, 3]]
        forest_graph = MagicMock()
        forest_graph.adj_list = {1: {2: 1.0, 3: 2.0}, 2: {1: 1.0}, 3: {1: 2.0}}
        forest_graph.trees = {1: MagicMock(tree_id=1, health_status=MagicMock(name='HEALTHY')), 2: MagicMock(tree_id=2, health_status=MagicMock(name='INFECTED')), 3: MagicMock(tree_id=3, health_status=MagicMock(name='AT_RISK'))}
        tree_positions = {1: (10, 10), 2: (20, 20), 3: (30, 30)}
        self.canvas.ax = MagicMock()
        self.canvas._shortest_path_highlight = [1, 2, 3]
        self.canvas.selected_tree = forest_graph.trees[1]
        self.canvas.path_start = forest_graph.trees[1]
        self.canvas._infection_labels = {2: "333"}
        self.canvas._infection_edge_highlight = {(1, 2)}
        self.canvas.draw_forest(forest_graph, tree_positions)
        self.canvas.ax.clear.assert_called()
        self.canvas.ax.set_xlim.assert_called()
        self.canvas.ax.set_ylim.assert_called()
        self.canvas.ax.set_aspect.assert_called()
        self.canvas.ax.grid.assert_called()
        self.canvas.ax.set_facecolor.assert_called()
        self.canvas.ax.add_patch.assert_called()
        self.canvas.ax.text.assert_called()
        self.canvas.ax.plot.assert_called()

    def test_draw_forest_empty(self):
        # Test with empty graph and positions
        forest_graph = MagicMock()
        forest_graph.adj_list = {}
        forest_graph.trees = {}
        tree_positions = {}
        self.canvas.ax = MagicMock()
        self.canvas.draw_forest(forest_graph, tree_positions)
        self.canvas.ax.clear.assert_called()

    def test_show_tooltip_with_existing(self):
        # Test show_tooltip when tooltip already exists
        self.canvas._tooltip = MagicMock()
        self.canvas.ax = MagicMock()
        self.canvas.canvas = MagicMock()
        self.canvas.show_tooltip(5, 5, "Tooltip")
        self.assertIsNotNone(self.canvas._tooltip)

    def test_hide_tooltip_with_exception(self):
        # Test hide_tooltip when draw_idle raises exception
        tooltip = MagicMock()
        tooltip.set_visible.side_effect = Exception("fail")
        self.canvas._tooltip = tooltip
        self.canvas.canvas = MagicMock()
        self.canvas.hide_tooltip()
        self.assertIsNone(self.canvas._tooltip)

    def test_get_emoji_font_all_branches(self):
        # Test all font branches
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Segoe UI Emoji')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'Segoe UI Emoji')
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Apple Color Emoji')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'Apple Color Emoji')
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Noto Color Emoji')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'Noto Color Emoji')
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Other Font')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'DejaVu Sans')

if __name__ == '__main__':
    unittest.main() 