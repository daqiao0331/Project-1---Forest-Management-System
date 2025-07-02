import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.dialogs.tree_dialogs import AddTreeDialog, DeleteTreeDialog, ModifyHealthDialog

class TestAddTreeDialog(unittest.TestCase):
    """
    Unit tests for the AddTreeDialog class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.dialogs.tree_dialogs.tk')
        patcher_ttk = patch('forest_management_system.gui.dialogs.tree_dialogs.ttk')
        patcher_messagebox = patch('forest_management_system.gui.dialogs.tree_dialogs.messagebox')
        patcher_health_status = patch('forest_management_system.gui.dialogs.tree_dialogs.HealthStatus')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.mock_messagebox = patcher_messagebox.start()
        self.mock_health_status = patcher_health_status.start()
        self.mock_health_status.HEALTHY = 'HEALTHY'
        self.mock_health_status.INFECTED = 'INFECTED'
        self.mock_health_status.AT_RISK = 'AT_RISK'
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.addCleanup(patcher_messagebox.stop)
        self.addCleanup(patcher_health_status.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that AddTreeDialog initializes the dialog and UI.
        """
        dialog = AddTreeDialog(self.parent)
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.species_var)
        self.assertIsNotNone(dialog.age_var)
        self.assertIsNotNone(dialog.health_var)
        dialog.dialog.title.assert_called_once()
        dialog.dialog.geometry.assert_called_once()
        dialog.dialog.configure.assert_called_once()
        dialog.dialog.transient.assert_called_once_with(self.parent)
        dialog.dialog.grab_set.assert_called_once()

    def test_on_ok_empty_species(self):
        """
        Test that _on_ok shows error if species is empty.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('')
        dialog.age_var.set('10')
        dialog.health_var.set('HEALTHY')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_age(self):
        """
        Test that _on_ok shows error if age is invalid.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('not_a_number')
        dialog.health_var.set('HEALTHY')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_negative_age(self):
        """
        Test that _on_ok shows error if age is negative.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('-10')
        dialog.health_var.set('HEALTHY')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_health_status(self):
        """
        Test that _on_ok shows error if health status is invalid.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('10')
        dialog.health_var.set('INVALID')
        self.mock_health_status.HEALTHY = 'HEALTHY'
        self.mock_health_status.INFECTED = 'INFECTED'
        self.mock_health_status.AT_RISK = 'AT_RISK'
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_success_healthy(self):
        """
        Test that _on_ok sets result with HEALTHY status and destroys dialog if input is valid.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('10')
        dialog.health_var.set('HEALTHY')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result["species"], 'Pine')
        self.assertEqual(dialog.result["age"], 10)
        self.assertEqual(dialog.result["health"], 'HEALTHY')
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_success_infected(self):
        """
        Test that _on_ok sets result with INFECTED status if input is valid.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('10')
        dialog.health_var.set('INFECTED')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result["species"], 'Pine')
        self.assertEqual(dialog.result["age"], 10)
        self.assertEqual(dialog.result["health"], 'INFECTED')
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_success_at_risk(self):
        """
        Test that _on_ok sets result with AT_RISK status if input is valid.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('10')
        dialog.health_var.set('AT_RISK')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result["species"], 'Pine')
        self.assertEqual(dialog.result["age"], 10)
        self.assertEqual(dialog.result["health"], 'AT_RISK')
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_destroy_exception(self):
        """
        Test that _on_ok handles exception if dialog.destroy fails.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.species_var.set('Pine')
        dialog.age_var.set('10')
        dialog.health_var.set('HEALTHY')
        dialog.dialog.destroy = MagicMock(side_effect=Exception('fail'))
        # Should not raise
        try:
            dialog._on_ok()
        except Exception:
            self.fail("_on_ok() raised Exception unexpectedly!")
        # Result should still be set
        self.assertIsNotNone(dialog.result)

    def test_show(self):
        """
        Test that show waits for window and returns result.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = {'species': 'Pine', 'age': 10, 'health': 'HEALTHY'}
        result = dialog.show()
        dialog.dialog.wait_window.assert_called_once()
        self.assertEqual(result, {'species': 'Pine', 'age': 10, 'health': 'HEALTHY'})

    def test_show_none_result(self):
        """
        Test that show returns None if result is None.
        """
        dialog = AddTreeDialog(self.parent)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = None
        result = dialog.show()
        self.assertIsNone(result)

class TestDeleteTreeDialog(unittest.TestCase):
    """
    Unit tests for the DeleteTreeDialog class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.dialogs.tree_dialogs.tk')
        patcher_ttk = patch('forest_management_system.gui.dialogs.tree_dialogs.ttk')
        patcher_messagebox = patch('forest_management_system.gui.dialogs.tree_dialogs.messagebox')
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
        Test that DeleteTreeDialog initializes the dialog and UI.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.tree_var)
        dialog.dialog.title.assert_called_once()
        dialog.dialog.geometry.assert_called_once()
        dialog.dialog.configure.assert_called_once()
        dialog.dialog.transient.assert_called_once_with(self.parent)
        dialog.dialog.grab_set.assert_called_once()

    def test_init_empty_tree_ids(self):
        """
        Test that DeleteTreeDialog initializes with empty tree_ids.
        """
        dialog = DeleteTreeDialog(self.parent, [])
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.tree_var)

    def test_on_ok_success(self):
        """
        Test that _on_ok sets result and destroys dialog if a tree is selected.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('1')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result, 1)
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_no_selection(self):
        """
        Test that _on_ok shows error if no tree is selected.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_id(self):
        """
        Test that _on_ok handles invalid tree id.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('abc')  # 非数字ID
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_destroy_exception(self):
        """
        Test that _on_ok handles exception if dialog.destroy fails.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('1')
        dialog.dialog.destroy = MagicMock(side_effect=Exception('fail'))
        # Should not raise
        try:
            dialog._on_ok()
        except Exception:
            self.fail("_on_ok() raised Exception unexpectedly!")
        # Result should still be set
        self.assertEqual(dialog.result, 1)

    def test_show(self):
        """
        Test that show waits for window and returns result.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = 1
        result = dialog.show()
        dialog.dialog.wait_window.assert_called_once()
        self.assertEqual(result, 1)

    def test_show_none_result(self):
        """
        Test that show returns None if result is None.
        """
        dialog = DeleteTreeDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = None
        result = dialog.show()
        self.assertIsNone(result)

class TestModifyHealthDialog(unittest.TestCase):
    """
    Unit tests for the ModifyHealthDialog class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.dialogs.tree_dialogs.tk')
        patcher_ttk = patch('forest_management_system.gui.dialogs.tree_dialogs.ttk')
        patcher_messagebox = patch('forest_management_system.gui.dialogs.tree_dialogs.messagebox')
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
        Test that ModifyHealthDialog initializes the dialog and UI.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.tree_var)
        self.assertIsNotNone(dialog.health_var)
        dialog.dialog.title.assert_called_once()
        dialog.dialog.geometry.assert_called_once()
        dialog.dialog.configure.assert_called_once()
        dialog.dialog.transient.assert_called_once_with(self.parent)
        dialog.dialog.grab_set.assert_called_once()

    def test_init_empty_tree_ids(self):
        """
        Test that ModifyHealthDialog initializes with empty tree_ids.
        """
        dialog = ModifyHealthDialog(self.parent, [])
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.tree_var)
        self.assertIsNotNone(dialog.health_var)

    def test_on_ok_success(self):
        """
        Test that _on_ok sets result and destroys dialog if input is valid.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('1')
        dialog.health_var.set('HEALTHY')
        dialog.dialog.destroy = MagicMock()
        dialog._on_ok()
        self.assertEqual(dialog.result["tree_id"], 1)
        self.assertEqual(dialog.result["health"], 'HEALTHY')
        dialog.dialog.destroy.assert_called_once()

    def test_on_ok_no_selection(self):
        """
        Test that _on_ok shows error if no tree is selected.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('')
        dialog.health_var.set('HEALTHY')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_no_health_selection(self):
        """
        Test that _on_ok shows error if no health status is selected.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('1')
        dialog.health_var.set('')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_invalid_tree_id(self):
        """
        Test that _on_ok handles invalid tree id.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('abc')  # 非数字ID
        dialog.health_var.set('HEALTHY')
        dialog._on_ok()
        self.mock_messagebox.showerror.assert_called()
        self.assertIsNone(dialog.result)

    def test_on_ok_destroy_exception(self):
        """
        Test that _on_ok handles exception if dialog.destroy fails.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.tree_var.set('1')
        dialog.health_var.set('HEALTHY')
        dialog.dialog.destroy = MagicMock(side_effect=Exception('fail'))
        # Should not raise
        try:
            dialog._on_ok()
        except Exception:
            self.fail("_on_ok() raised Exception unexpectedly!")
        # Result should still be set
        self.assertIsNotNone(dialog.result)

    def test_show(self):
        """
        Test that show waits for window and returns result.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = {'tree_id': 1, 'health': 'HEALTHY'}
        result = dialog.show()
        dialog.dialog.wait_window.assert_called_once()
        self.assertEqual(result, {'tree_id': 1, 'health': 'HEALTHY'})

    def test_show_none_result(self):
        """
        Test that show returns None if result is None.
        """
        dialog = ModifyHealthDialog(self.parent, self.tree_ids)
        dialog.dialog.wait_window = MagicMock()
        dialog.result = None
        result = dialog.show()
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 