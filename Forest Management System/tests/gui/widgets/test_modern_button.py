import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.widgets.modern_button import ModernButton

class TestModernButton(unittest.TestCase):
    """
    Unit tests for the ModernButton class.
    """
    def setUp(self):
        patcher_ttk = patch('forest_management_system.gui.widgets.modern_button.ttk')
        self.mock_ttk = patcher_ttk.start()
        self.addCleanup(patcher_ttk.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that ModernButton initializes as a ttk.Button.
        """
        button = ModernButton(self.parent)
        self.assertIsNotNone(button)

if __name__ == '__main__':
    unittest.main() 