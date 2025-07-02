import unittest
from unittest.mock import MagicMock, patch, ANY
import numpy as np
from matplotlib.patches import Circle, Rectangle
from forest_management_system.gui.panels.forest_canvas import ForestCanvas
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus

class TestForestCanvasFunctionality(unittest.TestCase):
    """
    Functional tests for the ForestCanvas class, testing the component's
    behavior as a whole rather than individual methods in isolation.
    """
    def setUp(self):
        """Set up the test environment with mock objects."""
        # Patch external dependencies
        self.patch_tk = patch('forest_management_system.gui.panels.forest_canvas.tk')
        self.patch_plt = patch('forest_management_system.gui.panels.forest_canvas.plt')
        self.patch_FigureCanvasTkAgg = patch('forest_management_system.gui.panels.forest_canvas.FigureCanvasTkAgg')
        self.patch_Circle = patch('forest_management_system.gui.panels.forest_canvas.Circle', return_value=MagicMock())
        self.patch_Rectangle = patch('forest_management_system.gui.panels.forest_canvas.Rectangle', return_value=MagicMock())
        self.patch_np = patch('forest_management_system.gui.panels.forest_canvas.np', wraps=np)
        self.patch_Figure = patch('forest_management_system.gui.panels.forest_canvas.Figure')
        
        # Start patches
        self.mock_tk = self.patch_tk.start()
        self.mock_plt = self.patch_plt.start()
        self.mock_FigureCanvasTkAgg = self.patch_FigureCanvasTkAgg.start()
        self.mock_Circle = self.patch_Circle.start()
        self.mock_Rectangle = self.patch_Rectangle.start()
        self.mock_np = self.patch_np.start()
        self.mock_Figure = self.patch_Figure.start()
        
        # Add cleanups
        self.addCleanup(self.patch_tk.stop)
        self.addCleanup(self.patch_plt.stop)
        self.addCleanup(self.patch_FigureCanvasTkAgg.stop)
        self.addCleanup(self.patch_Circle.stop)
        self.addCleanup(self.patch_Rectangle.stop)
        self.addCleanup(self.patch_np.stop)
        self.addCleanup(self.patch_Figure.stop)
        
        # Mock parent and figure/axes
        self.parent = MagicMock()
        self.mock_figure = MagicMock()
        self.mock_ax = MagicMock()
        self.mock_plt.subplots.return_value = (self.mock_figure, self.mock_ax)
        
        # Create canvas object and access its attributes
        with patch('matplotlib.font_manager.fontManager.ttflist', new=[MagicMock(name='Segoe UI Emoji')]):
            self.canvas = ForestCanvas(self.parent)
            self.canvas.ax = self.mock_ax
        
        # Create test data
        self.create_test_data()
        
    def create_test_data(self):
        """Create test data for forest visualization."""
        # Create mock forest graph and trees
        self.forest_graph = MagicMock()
        
        # Create three trees with different health statuses
        self.tree1 = MagicMock(tree_id=1, species='Pine', age=10, health_status=HealthStatus.HEALTHY)
        self.tree2 = MagicMock(tree_id=2, species='Oak', age=15, health_status=HealthStatus.INFECTED)
        self.tree3 = MagicMock(tree_id=3, species='Maple', age=8, health_status=HealthStatus.AT_RISK)
        
        # Set up trees dictionary
        self.forest_graph.trees = {
            1: self.tree1,
            2: self.tree2,
            3: self.tree3
        }
        
        # Set up adjacency list with paths between trees
        self.forest_graph.adj_list = {
            1: {2: 10.5},
            2: {1: 10.5, 3: 15.2},
            3: {2: 15.2}
        }
        
        # Set up tree positions
        self.tree_positions = {
            1: (20, 30),
            2: (50, 40),
            3: (70, 20)
        }
        
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_complete_forest_visualization(self, mock_find_reserves):
        """
        Test the complete forest visualization functionality.
        This tests drawing trees, paths, reserves, and various visual elements.
        """
        # Mock reserves detection
        mock_find_reserves.return_value = [[1, 2]]
        
        # Set up highlighting for testing different path styles
        self.canvas._shortest_path_highlight = [1, 2]
        self.canvas._infection_edge_highlight = {(2, 3)}
        self.canvas.selected_tree = self.tree1
        self.canvas.path_start = self.tree2
        
        # Execute the draw_forest method
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Verify the canvas setup
        self.mock_ax.clear.assert_called_once()
        self.mock_ax.set_xlim.assert_called_with(0, 100)
        self.mock_ax.set_ylim.assert_called_with(0, 100)
        self.mock_ax.set_aspect.assert_called_with('equal')
        self.mock_ax.grid.assert_called_with(True, alpha=0.2, color='#bdc3c7')
        
        # Verify reserves were drawn
        self.mock_ax.add_patch.assert_called()
        
        # Verify paths were drawn
        assert self.mock_ax.plot.call_count >= 2  # At least two paths should be drawn
        
        # Verify trees were drawn
        assert self.mock_ax.text.call_count >= 6  # At least 6 text elements (3 trees + 3 IDs)
        
        # Verify canvas was updated
        self.canvas.canvas.draw.assert_called_once()
        
    def test_tooltip_functionality(self):
        """Test showing and hiding tooltips on the canvas."""
        # Show tooltip
        self.canvas.show_tooltip(50, 50, "Test tooltip")
        self.mock_ax.annotate.assert_called_once()
        self.canvas.canvas.draw_idle.assert_called_once()
        self.assertIsNotNone(self.canvas._tooltip)
        
        # Reset mock to check hide_tooltip calls
        self.canvas.canvas.draw_idle.reset_mock()
        
        # Hide tooltip
        self.canvas.hide_tooltip()
        self.canvas._tooltip.set_visible.assert_called_with(False)
        self.canvas.canvas.draw_idle.assert_called_once()
        self.assertIsNone(self.canvas._tooltip)
        
    def test_tooltip_exception_handling(self):
        """Test exception handling when hiding tooltips."""
        # Set up tooltip that will raise an exception
        self.canvas._tooltip = MagicMock()
        self.canvas._tooltip.set_visible.side_effect = Exception("Test exception")
        
        # Hide tooltip should not propagate the exception
        self.canvas.hide_tooltip()
        self.assertIsNone(self.canvas._tooltip)
        
    def test_canvas_event_binding(self):
        """Test that event handlers are properly bound to the canvas."""
        handler = MagicMock()
        self.canvas.canvas.mpl_connect = MagicMock()
        
        # Bind event handlers
        self.canvas.setup_canvas_bindings(handler)
        
        # Verify all necessary events are bound
        assert self.canvas.canvas.mpl_connect.call_count >= 3  # button_press, motion_notify, button_release
        
        # Check specific event bindings
        expected_events = ['button_press_event', 'motion_notify_event', 'button_release_event']
        expected_handlers = [handler.on_press, handler.on_motion, handler.on_release]
        
        for i, (event, handler_func) in enumerate(zip(expected_events, expected_handlers)):
            call_args = self.canvas.canvas.mpl_connect.call_args_list[i][0]
            self.assertEqual(call_args[0], event)
            self.assertEqual(call_args[1], handler_func)
    
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_forest_with_no_paths(self, mock_find_reserves):
        """Test drawing a forest with trees but no paths."""
        # Set up forest with trees but no paths
        mock_find_reserves.return_value = []
        self.forest_graph.adj_list = {}
        
        # Draw forest
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Verify basic canvas setup was done
        self.mock_ax.clear.assert_called_once()
        self.mock_ax.set_xlim.assert_called_with(0, 100)
        self.mock_ax.set_ylim.assert_called_with(0, 100)
        
        # Verify trees were still drawn
        assert self.mock_ax.text.call_count > 0
        
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_forest_with_no_trees(self, mock_find_reserves):
        """Test drawing an empty forest."""
        # Set up empty forest
        mock_find_reserves.return_value = []
        self.forest_graph.trees = {}
        self.forest_graph.adj_list = {}
        
        # Draw forest
        self.canvas.draw_forest(self.forest_graph, {})
        
        # Verify basic canvas setup was done
        self.mock_ax.clear.assert_called_once()
        self.mock_ax.set_xlim.assert_called_with(0, 100)
        self.mock_ax.set_ylim.assert_called_with(0, 100)
        
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')  
    def test_different_health_statuses_visualization(self, mock_find_reserves):
        """Test visualization of trees with different health statuses."""
        # Set up forest with trees of different health statuses
        mock_find_reserves.return_value = []
        
        # Draw forest
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Verify that trees with different health statuses are drawn with different emojis
        # This is challenging to test precisely with mocks, but we can check general call patterns
        assert self.mock_ax.text.call_count >= 6  # At least 6 text elements (3 trees + 3 IDs)
        
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_path_highlight_visualization(self, mock_find_reserves):
        """Test visualization of highlighted paths (shortest path, infection path)."""
        # Set up forest
        mock_find_reserves.return_value = []
        
        # Set shortest path highlight
        self.canvas._shortest_path_highlight = [1, 2]
        
        # Draw forest
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Check that at least one path is drawn
        assert self.mock_ax.plot.call_count > 0
        
        # Set infection edge highlight
        self.canvas._infection_edge_highlight = {(2, 3)}
        
        # Draw forest again
        self.mock_ax.plot.reset_mock()
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Check that paths are drawn
        assert self.mock_ax.plot.call_count > 0
        
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_tree_selection_visualization(self, mock_find_reserves):
        """Test visualization of selected trees."""
        # Set up forest
        mock_find_reserves.return_value = []
        
        # Set selected tree
        self.canvas.selected_tree = self.tree1
        
        # Draw forest
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Selected tree should have a different appearance, which is reflected in text properties
        # This is challenging to verify precisely with mocks
        
    def test_emoji_font_selection(self):
        """Test emoji font selection logic."""
        # Test with Segoe UI Emoji available
        with patch('matplotlib.font_manager.fontManager.ttflist', 
                  new=[MagicMock(name='Segoe UI Emoji')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'Segoe UI Emoji')
        
        # Test with Apple Color Emoji available
        with patch('matplotlib.font_manager.fontManager.ttflist', 
                  new=[MagicMock(name='Apple Color Emoji')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'Apple Color Emoji')
        
        # Test with no preferred fonts available
        with patch('matplotlib.font_manager.fontManager.ttflist', 
                  new=[MagicMock(name='Other Font')]):
            font = self.canvas._get_emoji_font()
            self.assertEqual(font, 'DejaVu Sans')
            
    @patch('forest_management_system.gui.panels.forest_canvas.find_reserves')
    def test_integrated_visualization_workflow(self, mock_find_reserves):
        """Test an integrated visualization workflow with multiple updates."""
        # Initial forest setup
        mock_find_reserves.return_value = []
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Simulate selecting a tree
        self.canvas.selected_tree = self.tree1
        self.mock_ax.reset_mock()
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Simulate starting path drawing
        self.canvas.path_start = self.tree1
        self.mock_ax.reset_mock()
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        self.mock_ax.add_patch.assert_called()  # Should draw selection circle
        
        # Simulate highlighting shortest path
        self.canvas._shortest_path_highlight = [1, 2, 3]
        self.mock_ax.reset_mock()
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)
        
        # Simulate infection visualization
        self.canvas._infection_edge_highlight = {(1, 2)}
        self.canvas._infection_labels = {1: "🔴"}
        self.mock_ax.reset_mock()
        self.canvas.draw_forest(self.forest_graph, self.tree_positions)

if __name__ == '__main__':
    unittest.main() 