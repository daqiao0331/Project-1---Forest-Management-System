import unittest
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.infection_simulation import simulate_infection
from forest_management_system.components.health_status import HealthStatus

class TestInfectionSimulation(unittest.TestCase):
    def setUp(self):
        self.graph = load_forest_from_files('data/forest_management_dataset-trees.csv', 'data/forest_management_dataset-paths.csv')

    def test_simulate_infection(self):
        # Find an infected tree as the start
        start = next(tid for tid, t in self.graph.trees.items() if t.health_status == HealthStatus.INFECTED)
        infected = simulate_infection(self.graph, start)
        self.assertIn(start, infected)
        # All infected trees应为可达
        for tid in infected:
            self.assertTrue(tid in self.graph.trees)

if __name__ == '__main__':
    unittest.main()
