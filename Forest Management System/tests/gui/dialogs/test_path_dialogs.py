import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.dialogs.path_dialogs import ShortestPathDialog

class TestShortestPathDialog(unittest.TestCase):
    """
    Unit tests for the ShortestPathDialog class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.dialogs.path_dialogs.tk')
        patcher_ttk = patch('forest_management_system.gui.dialogs.path_dialogs.ttk')
        patcher_messagebox = patch('forest_management_system.gui.dialogs.path_dialogs.messagebox')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.mock_messagebox = patcher_messagebox.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.addCleanup(patcher_messagebox.stop)
        self.parent = MagicMock()
        self.tree_ids = [1, 2, 3]

    def test_init(self):
        """
        Test that ShortestPathDialog initializes the dialog and UI.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.start_var)
        self.assertIsNotNone(dialog.end_var)
        dialog.dialog.title.assert_called_once()
        dialog.dialog.geometry.assert_called_once()
        dialog.dialog.configure.assert_called_once()
        dialog.dialog.transient.assert_called_once_with(self.parent)
        dialog.dialog.grab_set.assert_called_once()

    def test_init_empty_tree_ids(self):
        """
        Test that ShortestPathDialog initializes with empty tree_ids.
        """
        dialog = ShortestPathDialog(self.parent, [])
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.start_var)
        self.assertIsNotNone(dialog.end_var)

    def test_on_ok_missing_selection(self):
        """
        Test that _on_ok shows error if start or end is missing.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('')
        dialog.end_var.set('')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_missing_start(self):
        """
        Test that _on_ok shows error if only start is missing.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('')
        dialog.end_var.set('2')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_missing_end(self):
        """
        Test that _on_ok shows error if only end is missing.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('1')
        dialog.end_var.set('')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_same_tree(self):
        """
        Test that _on_ok shows warning if start and end are the same.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('1')
        dialog.end_var.set('1')
        dialog._on_ok()
        self.mock_messagebox.showwarning.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_id(self):
        """
        Test that _on_ok shows error if tree id is invalid.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('abc')
        dialog.end_var.set('2')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_end_id(self):
        """
        Test that _on_ok shows error if end tree id is invalid.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('1')
        dialog.end_var.set('abc')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_success(self):
        """
        Test that _on_ok sets result and destroys dialog if input is valid.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('1')
        dialog.end_var.set('2')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result, (1, 2))
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_destroy_exception(self):
        """
        Test that _on_ok handles exception if dialog.destroy fails.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.start_var.set('1')
        dialog.end_var.set('2')
        dialog.dialog.destroy = MagicMock(side_effect=Exception('fail'))
        # Should not raise
        try:
            dialog._on_ok()
        except Exception:
            self.fail("_on_ok() raised Exception unexpectedly!")
        # Result should still be set
        self.assertEqual(dialog.result, (1, 2))

    def test_show(self):
        """
        Test that show waits for window and returns result.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = (1, 2)
        result = dialog.show()
        dialog.dialog.wait_window.assert_called_once()
        self.assertEqual(result, (1, 2))

    def test_show_none_result(self):
        """
        Test that show returns None if result is None.
        """
        dialog = ShortestPathDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = None
        result = dialog.show()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 