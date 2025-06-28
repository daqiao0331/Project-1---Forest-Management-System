import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.reserve_detection import find_reserves
from forest_management_system.components.health_status import HealthStatus

class TestReserveDetection(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        trees_file = os.path.join(base_dir, 'data', 'forest_management_dataset-trees.csv')
        paths_file = os.path.join(base_dir, 'data', 'forest_management_dataset-paths.csv')
        self.graph = load_forest_from_files(trees_file, paths_file)

    def test_find_reserves(self):
        reserves = find_reserves(self.graph)
        for reserve in reserves:
            for tid in reserve:
                self.assertEqual(self.graph.trees[tid].health_status, HealthStatus.HEALTHY)

if __name__ == '__main__':
    unittest.main()
