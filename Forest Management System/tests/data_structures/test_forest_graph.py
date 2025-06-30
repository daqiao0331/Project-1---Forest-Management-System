"""
Tests for the ForestGraph class to verify core functionality and edge cases.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.data_structures.path import Path
from forest_management_system.data_structures.forest_graph import ForestGraph

class TestForestGraph(unittest.TestCase):
    """Test cases for the ForestGraph class including base functionality and edge cases."""
    
    def setUp(self):
        """
        Set up test environment for each test with trees and a graph.
        """
        self.t1 = Tree(1, 'Oak', 10, HealthStatus.HEALTHY)
        self.t2 = Tree(2, 'Pine', 8, HealthStatus.INFECTED)
        self.t3 = Tree(3, 'Birch', 5, HealthStatus.AT_RISK)
        self.g = ForestGraph()
        self.g.add_tree(self.t1)
        self.g.add_tree(self.t2)
        self.g.add_tree(self.t3)

    def test_add_and_remove_tree(self):
        """
        Test adding and removing trees from the forest graph.
        Verifies basic tree management operations.
        """
        self.g.remove_tree(2)
        self.assertNotIn(2, self.g.trees)
        self.g.add_tree(self.t2)
        self.assertIn(2, self.g.trees)

    def test_overwrite_tree(self):
        """
        Test overwriting a tree with the same ID.
        Verifies that new tree overwrites old one while maintaining connections.
        """
        # Create a new tree with an existing ID
        new_tree2 = Tree(2, "Cedar", 80, HealthStatus.HEALTHY)
        
        # Add a path before overwriting
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        
        # Add the new tree (should overwrite the old one)
        self.g.add_tree(new_tree2)
        
        # Verify the tree was overwritten
        self.assertEqual(self.g.trees[2].species, "Cedar")
        self.assertEqual(self.g.trees[2].age, 80)
        self.assertEqual(self.g.trees[2].health_status, HealthStatus.HEALTHY)
        
        # Verify connections remain
        self.assertTrue(2 in self.g.adj_list[1])
        self.assertTrue(1 in self.g.adj_list[2])

    def test_remove_nonexistent_tree(self):
        """
        Test removing a tree that doesn't exist.
        Verifies graceful handling of non-existent tree removal.
        """
        # Count trees before
        trees_before = len(self.g.trees)
        
        # Try to remove a non-existent tree
        self.g.remove_tree(999)
        
        # Verify nothing changed
        self.assertEqual(len(self.g.trees), trees_before)

    def test_remove_tree_with_connections(self):
        """
        Test removing a tree that has connections to other trees.
        Verifies all connections are properly cleaned up.
        """
        # Add paths to connect trees
        self.g.add_path(Path(self.t1, self.t2, 5.0))
        self.g.add_path(Path(self.t2, self.t3, 10.0))
        
        # Remove tree 2 which is connected to both tree 1 and tree 3
        self.g.remove_tree(2)
        
        # Verify tree 2 is gone
        self.assertFalse(2 in self.g.trees)
        
        # Verify connections to tree 2 are gone
        self.assertFalse(2 in self.g.adj_list.get(1, {}))
        self.assertFalse(1 in self.g.adj_list.get(2, {}))
        self.assertFalse(3 in self.g.adj_list.get(2, {}))
        self.assertFalse(2 in self.g.adj_list.get(3, {}))

    def test_add_and_remove_path(self):
        """
        Test adding and removing paths between trees.
        Verifies basic path management.
        """
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        self.assertIn(2, self.g.adj_list[1])
        self.assertIn(1, self.g.adj_list[2])
        
        self.g.remove_path(1, 2)
        self.assertNotIn(2, self.g.adj_list[1])
        self.assertNotIn(1, self.g.adj_list[2])

    def test_add_duplicate_path(self):
        """
        Test adding a path between trees that already have a connection.
        Verifies weight is updated rather than creating duplicate.
        """
        # Add initial path
        self.g.add_path(Path(self.t1, self.t2, 5.0))
        
        # Count edges before
        edge_count_before = sum(len(neighbors) for neighbors in self.g.adj_list.values())
        
        # Create a new path with a different weight
        duplicate_path = Path(self.t1, self.t2, 20.0)
        
        # Add the duplicate path
        self.g.add_path(duplicate_path)
        
        # Verify the edge count remained the same (path was updated, not added)
        edge_count_after = sum(len(neighbors) for neighbors in self.g.adj_list.values())
        self.assertEqual(edge_count_after, edge_count_before)
        
        # Verify the weight was updated
        self.assertEqual(self.g.get_distance(1, 2), 20.0)

    def test_update_distance(self):
        """
        Test updating the distance between two trees.
        Verifies path weight can be changed after creation.
        """
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        self.g.update_distance(1, 2, 10.0)
        self.assertEqual(self.g.get_distance(1, 2), 10.0)

    def test_update_nonexistent_path(self):
        """
        Test updating a path that doesn't exist.
        Verifies graceful handling when updating non-existent path.
        """
        # Update non-existent path
        self.g.update_distance(1, 999, 30.0)
        
        # Verify it had no effect (no crash or exception)
        self.assertEqual(self.g.get_distance(1, 999), float('inf'))

    def test_get_neighbors_nonexistent_tree(self):
        """
        Test getting neighbors of a non-existent tree.
        Verifies empty list is returned for non-existent tree.
        """
        neighbors = self.g.get_neighbors(999)
        self.assertEqual(neighbors, [])

    def test_remove_nonexistent_path(self):
        """
        Test removing a path that doesn't exist.
        Verifies graceful handling when removing non-existent path.
        """
        # Count edges before
        edge_count_before = sum(len(neighbors) for neighbors in self.g.adj_list.values())
        
        # Remove non-existent path
        self.g.remove_path(1, 999)
        
        # Verify nothing changed
        edge_count_after = sum(len(neighbors) for neighbors in self.g.adj_list.values())
        self.assertEqual(edge_count_after, edge_count_before)

    def test_update_health_status(self):
        """
        Test updating the health status of a tree.
        Verifies tree health status can be changed after creation.
        """
        self.g.update_health_status(1, HealthStatus.INFECTED)
        self.assertEqual(self.g.trees[1].health_status, HealthStatus.INFECTED)

    def test_update_health_status_nonexistent_tree(self):
        """
        Test updating health status of a non-existent tree.
        Verifies graceful handling when updating non-existent tree.
        """
        # Update health status of non-existent tree
        self.g.update_health_status(999, HealthStatus.INFECTED)
        
        # Should not crash or raise an exception
        self.assertFalse(999 in self.g.trees)

    def test_clear_graph(self):
        """
        Test clearing the entire graph.
        Verifies all trees and paths are removed.
        """
        # Add some paths
        self.g.add_path(Path(self.t1, self.t2, 5.0))
        
        # Clear the graph
        self.g.clear()
        
        # Verify everything is gone
        self.assertEqual(len(self.g.trees), 0)
        self.assertEqual(len(self.g.adj_list), 0)

    def test_repr(self):
        """
        Test the string representation of the forest graph.
        Verifies basic representation information.
        """
        p = Path(self.t1, self.t2, 5.0)
        self.g.add_path(p)
        s = repr(self.g)
        self.assertIn('ForestGraph', s)
        self.assertIn('Adjacency List', s)
        
        # Additional verification of string representation content
        self.assertIn('1', s)
        self.assertIn('2', s)
        self.assertIn('3', s)

if __name__ == '__main__':
    unittest.main()
