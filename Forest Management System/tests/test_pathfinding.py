import unittest
from project_name.dataset_loader import load_forest_from_files
from project_name.pathfinding import find_shortest_path

class TestPathfinding(unittest.TestCase):
    def setUp(self):
        self.graph = load_forest_from_files('data/forest_management_dataset-trees.csv', 'data/forest_management_dataset-paths.csv')

    def test_find_shortest_path(self):
        # Pick two different trees
        tree_ids = list(self.graph.trees.keys())
        if len(tree_ids) >= 2:
            path, dist = find_shortest_path(self.graph, tree_ids[0], tree_ids[1])
            self.assertTrue(path[0] == tree_ids[0] and path[-1] == tree_ids[1])
            self.assertTrue(dist >= 0)

if __name__ == '__main__':
    unittest.main()
