import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.tree import Tree
from forest_management_system.components.utils import find_trees_by_health, count_trees_by_species
from forest_management_system.components.health_status import HealthStatus

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.trees = [
            Tree(1, 'Pine', 10, HealthStatus.HEALTHY),
            Tree(2, 'Oak', 5, HealthStatus.INFECTED),
            Tree(3, 'Pine', 7, HealthStatus.HEALTHY),
        ]

    def test_find_trees_by_health(self):
        healthy = find_trees_by_health(self.trees, HealthStatus.HEALTHY)
        self.assertEqual(len(healthy), 2)

    def test_count_trees_by_species(self):
        species_count = count_trees_by_species(self.trees)
        self.assertEqual(species_count['Pine'], 2)
        self.assertEqual(species_count['Oak'], 1)

if __name__ == '__main__':
    unittest.main()
