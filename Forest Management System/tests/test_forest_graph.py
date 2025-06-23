import unittest
from project_name.tree import Tree
from project_name.health_status import HealthStatus
from project_name.path import Path
from project_name.forest_graph import ForestGraph

class TestForestGraph(unittest.TestCase):
    def setUp(self):
        self.t1 = Tree(1, 'Oak', 10, HealthStatus.HEALTHY)
        self.t2 = Tree(2, 'Pine', 8, HealthStatus.INFECTED)
        self.t3 = Tree(3, 'Birch', 5, HealthStatus.AT_RISK)
        self.g = ForestGraph()
        self.g.add_tree(self.t1)
        self.g.add_tree(self.t2)
        self.g.add_tree(self.t3)

    def test_add_and_remove_tree(self):
        self.g.remove_tree(2)
        self.assertNotIn(2, self.g.trees)
        self.g.add_tree(self.t2)
        self.assertIn(2, self.g.trees)

    def test_add_and_remove_path(self):
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        self.assertIn(p, self.g.paths)
        self.g.remove_path(1, 2)
        self.assertNotIn(p, self.g.paths)

    def test_update_distance(self):
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        self.g.update_distance(1, 2, 10.0)
        self.assertEqual(self.g.paths[0].weight, 10.0)

    def test_update_health_status(self):
        self.g.update_health_status(1, HealthStatus.INFECTED)
        self.assertEqual(self.g.trees[1].health_status, HealthStatus.INFECTED)

    def test_repr(self):
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        s = repr(self.g)
        self.assertIn('ForestGraph', s)
        self.assertIn('Paths', s)

if __name__ == '__main__':
    unittest.main()
