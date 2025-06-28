import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.tree import Tree
from forest_management_system.components.health_status import HealthStatus
from forest_management_system.components.path import Path

class TestPath(unittest.TestCase):
    def setUp(self):
        self.t1 = Tree(1, 'Oak', 10, HealthStatus.HEALTHY)
        self.t2 = Tree(2, 'Pine', 8, HealthStatus.INFECTED)

    def test_path_init(self):
        p = Path(self.t1, self.t2, 5.0)
        self.assertEqual(p.tree1, self.t1)
        self.assertEqual(p.tree2, self.t2)
        self.assertEqual(p.weight, 5.0)

    def test_path_equality(self):
        p1 = Path(self.t1, self.t2, 5.0)
        p2 = Path(self.t2, self.t1, 5.0)
        self.assertEqual(p1, p2)

    def test_path_repr(self):
        p = Path(self.t1, self.t2, 5.0)
        s = repr(p)
        self.assertIn('Path', s)
        self.assertIn('distance', s)

if __name__ == '__main__':
    unittest.main()
