import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from forest_management_system.components.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.pathfinding import find_shortest_path

class TestPathfinding(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        trees_file = os.path.join(base_dir, 'data', 'forest_management_dataset-trees.csv')
        paths_file = os.path.join(base_dir, 'data', 'forest_management_dataset-paths.csv')
        self.graph = load_forest_from_files(trees_file, paths_file)

    def test_find_shortest_path(self):
        # Pick two different trees
        tree_ids = list(self.graph.trees.keys())
        if len(tree_ids) >= 2:
            path, dist = find_shortest_path(self.graph, tree_ids[0], tree_ids[1])
            self.assertTrue(path[0] == tree_ids[0] and path[-1] == tree_ids[1])
            self.assertTrue(dist >= 0)

if __name__ == '__main__':
    unittest.main()
