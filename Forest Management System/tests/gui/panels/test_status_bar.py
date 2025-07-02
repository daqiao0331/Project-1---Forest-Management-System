import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.panels.status_bar import StatusBar

class TestStatusBar(unittest.TestCase):
    """
    Unit tests for the StatusBar class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.panels.status_bar.tk')
        patcher_ttk = patch('forest_management_system.gui.panels.status_bar.ttk')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that StatusBar initializes the status bar and UI.
        """
        bar = StatusBar(self.parent)
        self.assertIsNotNone(bar)

    # Add more tests for public methods if available

if __name__ == '__main__':
    unittest.main() 