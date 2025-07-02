import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.panels.status_bar import StatusBar

class TestStatusBar(unittest.TestCase):
    """
    Unit tests for the StatusBar class.
    """
    def setUp(self):
        # 
        patcher_tk = patch('forest_management_system.gui.panels.status_bar.tk')
        self.mock_tk = patcher_tk.start()
        self.addCleanup(patcher_tk.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that StatusBar initializes the status bar and UI.
        """
        bar = StatusBar(self.parent)
        self.assertIsNotNone(bar)
        
        
        self.mock_tk.Label.assert_called_once()
        
    def test_set_text(self):
        """
        Test that set_text updates the status bar text.
        """
        bar = StatusBar(self.parent)
        bar.set_text("Testing status")
        bar.label.config.assert_called_once_with(text="Testing status")

if __name__ == '__main__':
    unittest.main() 