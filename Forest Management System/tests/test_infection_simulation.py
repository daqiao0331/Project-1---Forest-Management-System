import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.infection_simulation import simulate_infection
from forest_management_system.components.health_status import HealthStatus

class TestInfectionSimulation(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        trees_file = os.path.join(base_dir, 'data', 'forest_management_dataset-trees.csv')
        paths_file = os.path.join(base_dir, 'data', 'forest_management_dataset-paths.csv')
        self.graph = load_forest_from_files(trees_file, paths_file)

    def test_simulate_infection(self):
        # Find an infected tree as the start
        start = next(tid for tid, t in self.graph.trees.items() if t.health_status == HealthStatus.INFECTED)
        infected = simulate_infection(self.graph, start)
        infected_ids = [item[0] for item in infected]
        self.assertIn(start, infected_ids)
        # All infected trees should be reachable
        for tid in infected_ids:
            self.assertTrue(tid in self.graph.trees)

if __name__ == '__main__':
    unittest.main()
