import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.tree import Tree
from forest_management_system.components.health_status import HealthStatus

class TestTree(unittest.TestCase):
    def test_tree_init(self):
        tree = Tree(1, 'Oak', 8, HealthStatus.HEALTHY, 'ForestA')
        self.assertEqual(tree.tree_id, 1)
        self.assertEqual(tree.species, 'Oak')
        self.assertEqual(tree.age, 8)
        self.assertEqual(tree.health_status, HealthStatus.HEALTHY)
        self.assertEqual(tree.forest, 'ForestA')

    def test_health_status_enum(self):
        with self.assertRaises(ValueError):
            Tree(2, 'Pine', 5, 'not_enum')

    def test_repr_and_eq(self):
        t1 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t2 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t3 = Tree(2, 'Pine', 5, HealthStatus.INFECTED)
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        self.assertIn('Tree', repr(t1))

    def test_lt(self):
        t1 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t2 = Tree(2, 'Pine', 5, HealthStatus.INFECTED)
        self.assertTrue(t1 < t2)

if __name__ == '__main__':
    unittest.main()
