import unittest
from project_name.tree import Tree
from project_name.health_status import HealthStatus
from project_name.path import Path

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
