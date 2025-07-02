import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.handlers.ui_actions import UIActions

class TestUIActions(unittest.TestCase):
    """
    Unit tests for the UIActions class.
    """
    def setUp(self):
        self.app = MagicMock()
        self.app.root = MagicMock()
        self.app.main_window.forest_canvas = MagicMock()
        self.app.main_window.control_panel = MagicMock()
        self.app.status_bar = MagicMock()
        self.app.forest_graph = MagicMock()
        self.app.tree_positions = {}
        self.app.update_display = MagicMock()
        self.app.canvas_handler = MagicMock()
        self.app.main_window.forest_canvas.path_start = None
        self.actions = UIActions(self.app)
        self.actions.canvas = self.app.main_window.forest_canvas
        self.actions.control_panel = self.app.main_window.control_panel

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    @patch('forest_management_system.gui.handlers.ui_actions.Tree')
    def test_add_tree(self, MockTree, MockAddTreeDialog):
        dialog = MockAddTreeDialog.return_value
        dialog.show.return_value = {"species": "Pine", "age": 10, "health": "HEALTHY"}
        self.app.forest_graph.trees = {}
        tree_instance = MockTree.return_value
        tree_instance.tree_id = 1
        
        self.actions.add_tree()
        
        MockAddTreeDialog.assert_called_once_with(self.app.root)
        dialog.show.assert_called_once()
        MockTree.assert_called_once()
        self.app.forest_graph.add_tree.assert_called_once_with(tree_instance)
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.AddTreeDialog')
    def test_add_tree_canceled(self, MockAddTreeDialog):
        dialog = MockAddTreeDialog.return_value
        dialog.show.return_value = None
        
        self.actions.add_tree()
        
        MockAddTreeDialog.assert_called_once_with(self.app.root)
        dialog.show.assert_called_once()
        self.app.forest_graph.add_tree.assert_not_called()
        self.app.update_display.assert_not_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_start_delete_tree_no_trees(self, mock_messagebox):
        self.app.forest_graph.trees = {}
        self.actions.start_delete_tree()
        mock_messagebox.showwarning.assert_called_once()
        self.assertFalse(hasattr(self.actions, 'delete_tree_mode') or self.actions.delete_tree_mode)

    def test_start_delete_tree_with_trees(self):
        self.app.forest_graph.trees = {1: MagicMock()}
        self.actions.start_delete_tree()
        self.assertTrue(self.actions.delete_tree_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.delete_tree_btn.config.assert_called()

    def test_exit_delete_tree(self):
        self.actions.delete_tree_mode = True
        self.actions.exit_delete_tree()
        self.assertFalse(self.actions.delete_tree_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.delete_tree_btn.config.assert_called()
        self.app.update_display.assert_called()

    def test_delete_tree_at_position_tree_found(self):
        tree = MagicMock(tree_id=1)
        self.app.canvas_handler._find_tree_at_position.return_value = tree
        self.actions.delete_tree_at_position(10, 10)
        self.app.forest_graph.remove_tree.assert_called_once_with(1)
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    def test_delete_tree_at_position_no_tree(self):
        self.app.canvas_handler._find_tree_at_position.return_value = None
        self.actions.delete_tree_at_position(10, 10)
        self.app.forest_graph.remove_tree.assert_not_called()
        self.app.update_display.assert_not_called()
        self.app.status_bar.set_text.assert_called_with("No tree found at the selected position.")

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    @patch('forest_management_system.gui.handlers.ui_actions.ModifyHealthDialog')
    def test_modify_health(self, MockModifyHealthDialog, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock()}
        dialog = MockModifyHealthDialog.return_value
        dialog.show.return_value = {"tree_id": 1, "health": "HEALTHY"}
        self.actions.modify_health()
        self.app.forest_graph.update_health_status.assert_called()
        self.app.update_display.assert_called()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    @patch('forest_management_system.gui.handlers.ui_actions.ModifyHealthDialog')
    def test_modify_health_canceled(self, MockModifyHealthDialog, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock()}
        dialog = MockModifyHealthDialog.return_value
        dialog.show.return_value = None
        self.actions.modify_health()
        self.app.forest_graph.update_health_status.assert_not_called()
        self.app.update_display.assert_not_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_modify_health_no_trees(self, mock_messagebox):
        self.app.forest_graph.trees = {}
        self.actions.modify_health()
        mock_messagebox.showwarning.assert_called_once()
        self.app.forest_graph.update_health_status.assert_not_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_start_add_path_not_enough_trees(self, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock()}
        self.actions.start_add_path()
        mock_messagebox.showwarning.assert_called_once()
        self.assertFalse(hasattr(self.actions, 'add_path_mode') or self.actions.add_path_mode)

    def test_start_add_path_enough_trees(self):
        self.app.forest_graph.trees = {1: MagicMock(), 2: MagicMock()}
        self.actions.start_add_path()
        self.assertTrue(self.actions.add_path_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.add_path_btn.config.assert_called()

    def test_exit_add_path(self):
        self.actions.add_path_mode = True
        self.actions.exit_add_path()
        self.assertFalse(self.actions.add_path_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.add_path_btn.config.assert_called()
        self.app.update_display.assert_called()

    def test_handle_path_point_selection_first(self):
        self.app.canvas_handler._find_tree_at_position.return_value = MagicMock(tree_id=1)
        self.actions.canvas.path_start = None
        self.actions.handle_path_point_selection(10, 10)
        self.assertEqual(self.actions.canvas.path_start.tree_id, 1)
        self.app.status_bar.set_text.assert_called()

    def test_handle_path_point_selection_no_tree(self):
        self.app.canvas_handler._find_tree_at_position.return_value = None
        self.actions.canvas.path_start = None
        self.actions.handle_path_point_selection(10, 10)
        self.assertIsNone(self.actions.canvas.path_start)
        self.app.status_bar.set_text.assert_called_with("No tree found at the selected position.")

    def test_handle_path_point_selection_second(self):
        tree1 = MagicMock(tree_id=1)
        tree2 = MagicMock(tree_id=2)
        self.app.canvas_handler._find_tree_at_position.return_value = tree2
        self.actions.canvas.path_start = tree1
        self.app.tree_positions = {1: (0, 0), 2: (3, 4)}
        self.app.forest_graph.add_path = MagicMock()
        self.actions.handle_path_point_selection(1, 1)
        self.app.forest_graph.add_path.assert_called()
        self.app.status_bar.set_text.assert_called()
        self.app.update_display.assert_called()
        self.assertIsNone(self.actions.canvas.path_start)

    def test_handle_path_point_selection_same_tree(self):
        tree1 = MagicMock(tree_id=1)
        self.app.canvas_handler._find_tree_at_position.return_value = tree1
        self.actions.canvas.path_start = tree1
        self.actions.handle_path_point_selection(1, 1)
        self.app.forest_graph.add_path.assert_not_called()
        self.app.status_bar.set_text.assert_called()
        self.assertEqual(self.actions.canvas.path_start, tree1)  # Should not reset the start tree

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_start_delete_path_no_paths(self, mock_messagebox):
        self.app.forest_graph.adj_list = {}
        self.actions.start_delete_path()
        mock_messagebox.showwarning.assert_called_once()
        self.assertFalse(hasattr(self.actions, 'delete_path_mode') or self.actions.delete_path_mode)

    def test_start_delete_path_with_paths(self):
        self.app.forest_graph.adj_list = {1: {2: 5.0}}
        self.actions.start_delete_path()
        self.assertTrue(self.actions.delete_path_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.delete_path_btn.config.assert_called()

    def test_exit_delete_path(self):
        self.actions.delete_path_mode = True
        self.actions.exit_delete_path()
        self.assertFalse(self.actions.delete_path_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.delete_path_btn.config.assert_called()

    def test_delete_path_at_position_path_found(self):
        path_mock = MagicMock()
        path_mock.tree1 = MagicMock(tree_id=1)
        path_mock.tree2 = MagicMock(tree_id=2)
        self.app.canvas_handler.find_path_at_position.return_value = path_mock
        self.actions.delete_path_at_position(10, 10)
        self.app.forest_graph.remove_path.assert_called_once_with(1, 2)
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    def test_delete_path_at_position_no_path(self):
        self.app.canvas_handler.find_path_at_position.return_value = None
        self.actions.delete_path_at_position(10, 10)
        self.app.forest_graph.remove_path.assert_not_called()
        self.app.update_display.assert_not_called()
        self.app.status_bar.set_text.assert_called_with("No path found at the selected position.")

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    @patch('forest_management_system.gui.handlers.ui_actions.ShortestPathDialog')
    @patch('forest_management_system.gui.handlers.ui_actions.find_shortest_path')
    def test_find_shortest_path(self, mock_find_shortest_path, MockShortestPathDialog, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock(), 2: MagicMock()}
        dialog = MockShortestPathDialog.return_value
        dialog.show.return_value = (1, 2)
        mock_find_shortest_path.return_value = ([1, 2], 5.0)
        self.actions.find_shortest_path()
        self.app.update_display.assert_called()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    @patch('forest_management_system.gui.handlers.ui_actions.ShortestPathDialog')
    @patch('forest_management_system.gui.handlers.ui_actions.find_shortest_path')
    def test_find_shortest_path_canceled(self, mock_find_shortest_path, MockShortestPathDialog, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock(), 2: MagicMock()}
        dialog = MockShortestPathDialog.return_value
        dialog.show.return_value = None
        self.actions.find_shortest_path()
        mock_find_shortest_path.assert_not_called()
        self.app.update_display.assert_not_called()

    @patch('forest_management_system.gui.handlers.ui_actions.messagebox')
    def test_find_shortest_path_not_enough_trees(self, mock_messagebox):
        self.app.forest_graph.trees = {1: MagicMock()}
        self.actions.find_shortest_path()
        mock_messagebox.showwarning.assert_called_once()

    @patch('forest_management_system.gui.handlers.ui_actions.LoadDataDialog')
    @patch('forest_management_system.gui.handlers.ui_actions.load_forest_from_files')
    def test_load_data(self, mock_load_forest, MockLoadDataDialog):
        dialog = MockLoadDataDialog.return_value
        dialog.show.return_value = ('tree.csv', 'path.csv')
        mock_load_forest.return_value = (MagicMock(), {})
        self.actions.load_data()
        mock_load_forest.assert_called_once_with('tree.csv', 'path.csv')
        self.app.tree_positions.clear.assert_called_once()

    @patch('forest_management_system.gui.handlers.ui_actions.LoadDataDialog')
    def test_load_data_canceled(self, MockLoadDataDialog):
        dialog = MockLoadDataDialog.return_value
        dialog.show.return_value = None
        self.actions.load_data()
        self.app.forest_graph.clear.assert_not_called()
        self.app.tree_positions.clear.assert_not_called()

    def test_restore_original_data(self):
        self.app.restore_snapshot = MagicMock(return_value=True)
        self.actions.restore_original_data()
        self.app.restore_snapshot.assert_called_once()
        self.app.status_bar.set_text.assert_called()
        self.actions.control_panel.restore_original_btn.config.assert_called()

    def test_restore_original_data_failed(self):
        self.app.restore_snapshot = MagicMock(return_value=False)
        self.actions.restore_original_data()
        self.app.restore_snapshot.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.filedialog')
    @patch('forest_management_system.gui.handlers.ui_actions.csv')
    def test_save_data(self, mock_csv, mock_filedialog):
        mock_filedialog.asksaveasfilename.return_value = 'test.csv'
        mock_csv_writer = MagicMock()
        mock_csv.writer.return_value = mock_csv_writer
        
        self.app.forest_graph.trees = {1: MagicMock(tree_id=1, species='Pine', age=10, health_status=MagicMock(name='HEALTHY'))}
        self.app.forest_graph.adj_list = {1: {2: 1.0}, 2: {1: 1.0}}
        self.app.tree_positions = {1: (10, 10), 2: (20, 20)}
        
        self.actions.save_data()
        mock_filedialog.asksaveasfilename.assert_called_once()
        mock_csv.writer.assert_called()
        mock_csv_writer.writerow.assert_called()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.filedialog')
    def test_save_data_canceled(self, mock_filedialog):
        mock_filedialog.asksaveasfilename.return_value = ''
        self.actions.save_data()
        self.app.status_bar.set_text.assert_called_with("Save operation canceled.")

    def test_clear_data(self):
        self.actions.clear_data()
        self.app.forest_graph.clear.assert_called_once()
        self.app.tree_positions.clear.assert_called_once()
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    def test_enter_exit_infection_sim_mode(self):
        self.actions.enter_infection_sim_mode()
        self.assertTrue(self.actions.infection_sim_mode)
        self.app.status_bar.set_text.assert_called()
        self.actions.exit_infection_sim_mode()
        self.assertFalse(self.actions.infection_sim_mode)
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.simulate_infection')
    def test_start_infection_at_position(self, mock_simulate_infection):
        tree = MagicMock(tree_id=1)
        self.app.canvas_handler._find_tree_at_position.return_value = tree
        mock_simulate_infection.return_value = (set(), set())
        self.actions.start_infection_at_position(10, 10)
        mock_simulate_infection.assert_called_once()
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    def test_start_infection_at_position_no_tree(self):
        self.app.canvas_handler._find_tree_at_position.return_value = None
        self.actions.start_infection_at_position(10, 10)
        self.app.update_display.assert_not_called()
        self.app.status_bar.set_text.assert_called_with("No tree found at the selected position.")

    @patch('forest_management_system.gui.handlers.ui_actions.find_reserves')
    def test_analyze_forest(self, mock_find_reserves):
        mock_find_reserves.return_value = [[1, 2], [3, 4]]
        self.app.forest_graph.trees = {1: MagicMock(), 2: MagicMock(), 3: MagicMock(), 4: MagicMock()}
        self.actions.analyze_forest()
        mock_find_reserves.assert_called_once_with(self.app.forest_graph)
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

    @patch('forest_management_system.gui.handlers.ui_actions.find_reserves')
    def test_analyze_forest_no_reserves(self, mock_find_reserves):
        mock_find_reserves.return_value = []
        self.app.forest_graph.trees = {1: MagicMock(), 2: MagicMock()}
        self.actions.analyze_forest()
        mock_find_reserves.assert_called_once_with(self.app.forest_graph)
        self.app.update_display.assert_called_once()
        self.app.status_bar.set_text.assert_called()

if __name__ == '__main__':
    unittest.main() 