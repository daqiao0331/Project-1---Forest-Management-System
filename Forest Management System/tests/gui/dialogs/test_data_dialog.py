import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.dialogs.data_dialog import LoadDataDialog

class TestLoadDataDialog(unittest.TestCase):
    """
    Unit tests for the LoadDataDialog class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.dialogs.data_dialog.tk')
        patcher_ttk = patch('forest_management_system.gui.dialogs.data_dialog.ttk')
        patcher_filedialog = patch('forest_management_system.gui.dialogs.data_dialog.filedialog')
        patcher_messagebox = patch('forest_management_system.gui.dialogs.data_dialog.messagebox')
        patcher_os = patch('forest_management_system.gui.dialogs.data_dialog.os')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.mock_filedialog = patcher_filedialog.start()
        self.mock_messagebox = patcher_messagebox.start()
        self.mock_os = patcher_os.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.addCleanup(patcher_filedialog.stop)
        self.addCleanup(patcher_messagebox.stop)
        self.addCleanup(patcher_os.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that LoadDataDialog initializes the dialog and UI.
        """
        dialog = LoadDataDialog(self.parent)
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.tree_file_var)
        self.assertIsNotNone(dialog.path_file_var)

    def test_setup_ui(self):
        """
        Test that _setup_ui runs without error (UI elements are created).
        """
        dialog = LoadDataDialog(self.parent)
        dialog._setup_ui()
        self.assertIsNotNone(dialog.tree_file_var)
        self.assertIsNotNone(dialog.path_file_var)

    def test_browse_tree_file(self):
        """
        Test that _browse_tree_file sets the tree file variable when a file is selected.
        """
        dialog = LoadDataDialog(self.parent)
        self.mock_filedialog.askopenfilename.return_value = '/tmp/tree.csv'
        dialog._browse_tree_file()
        self.assertEqual(dialog.tree_file_var.get(), '/tmp/tree.csv')

    def test_browse_path_file(self):
        """
        Test that _browse_path_file sets the path file variable when a file is selected.
        """
        dialog = LoadDataDialog(self.parent)
        self.mock_filedialog.askopenfilename.return_value = '/tmp/path.csv'
        dialog._browse_path_file()
        self.assertEqual(dialog.path_file_var.get(), '/tmp/path.csv')

    def test_browse_tree_file_cancel(self):
        """
        Test that _browse_tree_file does nothing if no file is selected.
        """
        dialog = LoadDataDialog(self.parent)
        self.mock_filedialog.askopenfilename.return_value = ''
        dialog.tree_file_var.set('old.csv')
        dialog._browse_tree_file()
        self.assertEqual(dialog.tree_file_var.get(), 'old.csv')

    def test_browse_path_file_cancel(self):
        """
        Test that _browse_path_file does nothing if no file is selected.
        """
        dialog = LoadDataDialog(self.parent)
        self.mock_filedialog.askopenfilename.return_value = ''
        dialog.path_file_var.set('old.csv')
        dialog._browse_path_file()
        self.assertEqual(dialog.path_file_var.get(), 'old.csv')

    def test_on_ok_missing_files(self):
        """
        Test that _on_ok shows error if files are missing.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('')
        dialog.path_file_var.set('')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()

    def test_on_ok_file_not_exists(self):
        """
        Test that _on_ok shows error if file does not exist.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('/not/exist/tree.csv')
        dialog.path_file_var.set('/not/exist/path.csv')
        self.mock_os.path.exists.return_value = False
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()

    def test_on_ok_tree_file_not_exists(self):
        """
        Test that _on_ok shows error if tree file does not exist.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('/not/exist/tree.csv')
        dialog.path_file_var.set('/tmp/path.csv')
        self.mock_os.path.exists.side_effect = lambda x: x == '/tmp/path.csv'
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()

    def test_on_ok_path_file_not_exists(self):
        """
        Test that _on_ok shows error if path file does not exist.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('/tmp/tree.csv')
        dialog.path_file_var.set('/not/exist/path.csv')
        self.mock_os.path.exists.side_effect = lambda x: x == '/tmp/tree.csv'
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()

    def test_on_ok_dialog_destroy_exception(self):
        """
        Test that _on_ok handles exception if dialog.destroy fails.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('/tmp/tree.csv')
        dialog.path_file_var.set('/tmp/path.csv')
        self.mock_os.path.exists.return_value = True
        dialog.dialog.destroy = MagicMock(side_effect=Exception('fail'))
        # Should not raise
        try:
            dialog._on_ok()
        except Exception:
            self.fail("_on_ok() raised Exception unexpectedly!")

    def test_on_ok_success(self):
        """
        Test that _on_ok sets result and destroys dialog if files exist.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.tree_file_var.set('/tmp/tree.csv')
        dialog.path_file_var.set('/tmp/path.csv')
        self.mock_os.path.exists.return_value = True
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result, ('/tmp/tree.csv', '/tmp/path.csv'))
        dialog.dialog.destroy.assert_called_once()

    def test_show(self):
        """
        Test that show waits for window and returns result.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = ('/tmp/tree.csv', '/tmp/path.csv')
        result = dialog.show()
        dialog.dialog.wait_window.assert_called_once()
        self.assertEqual(result, ('/tmp/tree.csv', '/tmp/path.csv'))

    def test_show_result_none(self):
        """
        Test that show returns None if result is not set.
        """
        dialog = LoadDataDialog(self.parent)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = None
        result = dialog.show()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 