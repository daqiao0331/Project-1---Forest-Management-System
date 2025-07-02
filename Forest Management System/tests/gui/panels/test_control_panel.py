import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.panels.control_panel import ControlPanel

class TestControlPanel(unittest.TestCase):
    """
    Unit tests for the ControlPanel class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.panels.control_panel.tk')
        patcher_ttk = patch('forest_management_system.gui.panels.control_panel.ttk')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.parent = MagicMock()

    def test_init(self):
        """
        Test that ControlPanel initializes the panel and UI.
        """
        panel = ControlPanel(self.parent)
        self.assertIsNotNone(panel)

    # Add more tests for public methods if available

if __name__ == '__main__':
    unittest.main() 