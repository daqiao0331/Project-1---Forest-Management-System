import unittest
from unittest.mock import MagicMock, patch
from forest_management_system.gui.panels.info_panel import InfoPanel

class TestInfoPanel(unittest.TestCase):
    """
    Unit tests for the InfoPanel class.
    """
    def setUp(self):
        patcher_tk = patch('forest_management_system.gui.panels.info_panel.tk')
        patcher_ttk = patch('forest_management_system.gui.panels.info_panel.ttk')
        self.mock_tk = patcher_tk.start()
        self.mock_ttk = patcher_ttk.start()
        self.addCleanup(patcher_tk.stop)
        self.addCleanup(patcher_ttk.stop)
        self.parent = MagicMock()
        self.panel = InfoPanel(self.parent)
        self.panel.info_text = MagicMock()

    def test_init(self):
        """
        Test that InfoPanel initializes the panel and UI.
        """
        self.assertIsNotNone(self.panel)

    def test_bind_mouse_wheel(self):
        event = MagicMock()
        self.panel.info_text.bind_all = MagicMock()
        self.panel._bind_mouse_wheel(event)
        self.panel.info_text.bind_all.assert_called_with('<MouseWheel>', self.panel._on_mouse_wheel)

    def test_unbind_mouse_wheel(self):
        event = MagicMock()
        self.panel.info_text.unbind_all = MagicMock()
        self.panel._unbind_mouse_wheel(event)
        self.panel.info_text.unbind_all.assert_called_with('<MouseWheel>')

    def test_on_mouse_wheel(self):
        event = MagicMock()
        event.delta = 120
        self.panel.info_text.yview_scroll = MagicMock()
        self.panel._on_mouse_wheel(event)
        self.panel.info_text.yview_scroll.assert_called()

    def test_update_info_normal(self):
        forest_graph = MagicMock()
        forest_graph.trees = {1: MagicMock(health_status=MagicMock(name='HEALTHY'), species='Pine')}
        forest_graph.adj_list = {1: {}}
        def fake_find_reserves(graph): return [[1]]
        self.panel.info_text.config = MagicMock()
        self.panel.info_text.delete = MagicMock()
        self.panel.info_text.insert = MagicMock()
        self.panel.update_info(forest_graph, fake_find_reserves)
        self.panel.info_text.insert.assert_called()
        self.panel.info_text.config.assert_called()

    def test_update_info_with_exception(self):
        forest_graph = MagicMock()
        forest_graph.trees = {1: MagicMock(health_status=MagicMock(name='HEALTHY'), species='Pine')}
        forest_graph.adj_list = {1: {}}
        def raise_exception(graph): raise Exception()
        self.panel.info_text.config = MagicMock()
        self.panel.info_text.delete = MagicMock()
        self.panel.info_text.insert = MagicMock()
        self.panel.update_info(forest_graph, raise_exception)
        self.panel.info_text.insert.assert_called()
        self.panel.info_text.config.assert_called()

if __name__ == '__main__':
    unittest.main() 