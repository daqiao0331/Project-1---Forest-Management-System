import unittest
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.reserve_detection import find_reserves
from forest_management_system.components.health_status import HealthStatus

class TestReserveDetection(unittest.TestCase):
    def setUp(self):
        self.graph = load_forest_from_files('data/forest_management_dataset-trees.csv', 'data/forest_management_dataset-paths.csv')

    def test_find_reserves(self):
        reserves = find_reserves(self.graph)
        for reserve in reserves:
            for tid in reserve:
                self.assertEqual(self.graph.trees[tid].health_status, HealthStatus.HEALTHY)

if __name__ == '__main__':
    unittest.main()
