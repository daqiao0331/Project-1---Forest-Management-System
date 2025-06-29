import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.io.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.pathfinding import find_shortest_path
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.path import Path
from forest_management_system.data_structures.forest_graph import ForestGraph
from forest_management_system.data_structures.health_status import HealthStatus

class TestPathfinding(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        trees_file = os.path.join(base_dir, 'data', 'forest_management_dataset-trees.csv')
        paths_file = os.path.join(base_dir, 'data', 'forest_management_dataset-paths.csv')
        try:
            self.graph = load_forest_from_files(trees_file, paths_file)
        except FileNotFoundError:
            # Create a test graph if data files don't exist
            self.graph = self.create_test_graph()

    def create_test_graph(self):
        """Create a test graph for testing when CSV files aren't available."""
        graph = ForestGraph()
        # Create trees
        trees = [
            Tree(1, "Pine", 10, HealthStatus.HEALTHY),
            Tree(2, "Oak", 15, HealthStatus.HEALTHY),
            Tree(3, "Maple", 8, HealthStatus.HEALTHY),
            Tree(4, "Pine", 12, HealthStatus.HEALTHY),
            Tree(5, "Oak", 20, HealthStatus.HEALTHY),
            Tree(6, "Birch", 5, HealthStatus.HEALTHY)  # Isolated tree
        ]
        
        # Add trees to graph
        for tree in trees:
            graph.add_tree(tree)
            
        # Create a simple path network:
        # 1 -- 10 -- 2
        # |           |
        # 15          5
        # |           |
        # 4 -- 8  --- 3
        #
        # 5 -- ? -- ? (should not be reachable)
        #
        # 6 (isolated)
        
        paths = [
            Path(trees[0], trees[1], 10.0),  # 1-2
            Path(trees[1], trees[2], 5.0),   # 2-3
            Path(trees[2], trees[3], 8.0),   # 3-4
            Path(trees[0], trees[3], 15.0),  # 1-4
            # Tree 5 has no paths (only to test disconnected components)
            # Tree 6 is isolated
        ]
        
        for path in paths:
            graph.add_path(path)
            
        return graph

    def test_find_shortest_path_basic(self):
        """Test finding shortest path between two connected trees."""
        # Pick two different trees
        tree_ids = list(self.graph.trees.keys())
        if len(tree_ids) >= 2:
            path, dist = find_shortest_path(self.graph, tree_ids[0], tree_ids[1])
            if dist != float('inf'):  # Only verify if a path exists
                self.assertEqual(path[0], tree_ids[0], "Path should start at the start tree")
                self.assertEqual(path[-1], tree_ids[1], "Path should end at the end tree")
                self.assertGreaterEqual(dist, 0, "Distance should be non-negative")
                
                # Check path continuity - each node should be connected to the previous one
                for i in range(1, len(path)):
                    prev_node = path[i-1]
                    curr_node = path[i]
                    neighbors = self.graph.get_neighbors(prev_node)
                    self.assertIn(curr_node, neighbors, 
                                 f"Path discontinuity: {prev_node} is not connected to {curr_node}")

    def test_find_shortest_path_same_tree(self):
        """Test finding shortest path from a tree to itself."""
        if len(self.graph.trees) > 0:
            tree_id = next(iter(self.graph.trees.keys()))
            path, dist = find_shortest_path(self.graph, tree_id, tree_id)
            self.assertEqual(path, [tree_id], "Path to self should only contain the tree itself")
            self.assertEqual(dist, 0, "Distance to self should be 0")

    def test_find_shortest_path_disconnected(self):
        """Test finding shortest path between disconnected trees."""
        # Create a graph with two disconnected components
        graph = self.create_test_graph()
        
        # Tree 1 and Tree 5 should not have a path between them
        path, dist = find_shortest_path(graph, 1, 5)
        self.assertEqual(path, [], "Path between disconnected trees should be empty")
        self.assertEqual(dist, float('inf'), "Distance between disconnected trees should be infinity")

    def test_find_shortest_path_isolated_tree(self):
        """Test finding shortest path to an isolated tree."""
        graph = self.create_test_graph()
        
        # Tree 6 is isolated
        path, dist = find_shortest_path(graph, 1, 6)
        self.assertEqual(path, [], "Path to isolated tree should be empty")
        self.assertEqual(dist, float('inf'), "Distance to isolated tree should be infinity")

    def test_find_shortest_path_invalid_tree(self):
        """Test finding shortest path with invalid tree IDs."""
        # Create an invalid tree ID
        invalid_id = max(self.graph.trees.keys()) + 1000
        
        # Test with invalid start
        path, dist = find_shortest_path(self.graph, invalid_id, 1)
        self.assertEqual(path, [], "Path with invalid start should be empty")
        self.assertEqual(dist, float('inf'), "Distance with invalid start should be infinity")
        
        # Test with invalid end
        path, dist = find_shortest_path(self.graph, 1, invalid_id)
        self.assertEqual(path, [], "Path with invalid end should be empty")
        self.assertEqual(dist, float('inf'), "Distance with invalid end should be infinity")
        
    def test_known_shortest_path(self):
        """Test with a graph where we know the expected shortest path."""
        graph = self.create_test_graph()
        
        # The shortest path from 1 to 3 should be 1-2-3 with distance 15
        # (going through 4 would be 1-4-3 with distance 23)
        path, dist = find_shortest_path(graph, 1, 3)
        
        self.assertEqual(path, [1, 2, 3], "Shortest path from 1 to 3 should be [1, 2, 3]")
        self.assertEqual(dist, 15.0, "Distance of shortest path should be 15")

if __name__ == '__main__':
    unittest.main()
