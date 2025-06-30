import unittest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.algorithms.reserve_detection import find_reserves
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.forest_graph import ForestGraph
from forest_management_system.data_structures.path import Path

class TestReserveDetection(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a forest graph with a known reserve.
        """
        # Create a forest graph for testing
        self.forest_graph = ForestGraph()
        
        # Add healthy trees that will form a reserve (trees 1, 2, 3)
        self.forest_graph.add_tree(Tree(1, "Oak", 10, HealthStatus.HEALTHY))
        self.forest_graph.add_tree(Tree(2, "Pine", 12, HealthStatus.HEALTHY))
        self.forest_graph.add_tree(Tree(3, "Maple", 15, HealthStatus.HEALTHY))
        
        # Add a complete graph between them
        tree1 = self.forest_graph.trees[1]
        tree2 = self.forest_graph.trees[2]
        tree3 = self.forest_graph.trees[3]
        
        self.forest_graph.add_path(Path(tree1, tree2, 10.0))
        self.forest_graph.add_path(Path(tree1, tree3, 11.0))
        self.forest_graph.add_path(Path(tree2, tree3, 12.0))
        
        # Add another set of healthy trees (4, 5, 6)
        self.forest_graph.add_tree(Tree(4, "Redwood", 20, HealthStatus.HEALTHY))
        self.forest_graph.add_tree(Tree(5, "Sequoia", 25, HealthStatus.HEALTHY))
        self.forest_graph.add_tree(Tree(6, "Cedar", 30, HealthStatus.HEALTHY))
        
        # Connect them in a complete graph
        tree4 = self.forest_graph.trees[4]
        tree5 = self.forest_graph.trees[5]
        tree6 = self.forest_graph.trees[6]
        
        self.forest_graph.add_path(Path(tree4, tree5, 15.0))
        self.forest_graph.add_path(Path(tree4, tree6, 16.0))
        self.forest_graph.add_path(Path(tree5, tree6, 17.0))
        
        # Add an unhealthy tree
        self.forest_graph.add_tree(Tree(7, "Birch", 5, HealthStatus.AT_RISK))
        
        # Connect unhealthy tree to one of the healthy trees, breaking its reserve status
        tree7 = self.forest_graph.trees[7]
        self.forest_graph.add_path(Path(tree3, tree7, 20.0))
        
        # Add another healthy tree but too small to form a reserve
        self.forest_graph.add_tree(Tree(8, "Ash", 10, HealthStatus.HEALTHY))
        self.forest_graph.add_tree(Tree(9, "Elm", 12, HealthStatus.HEALTHY))
        tree8 = self.forest_graph.trees[8]
        tree9 = self.forest_graph.trees[9]
        self.forest_graph.add_path(Path(tree8, tree9, 5.0))

    def test_find_reserves(self):
        """
        Test the basic functionality of finding reserves in a forest.
        Verifies that all trees in every identified reserve are healthy.
        """
        # Get reserves from our test forest
        reserves = find_reserves(self.forest_graph)
        
        # Should find exactly one reserve (4, 5, 6)
        self.assertEqual(len(reserves), 1)
        
        # The reserve should contain trees 4, 5, 6
        reserve = reserves[0]  # Get the first (and only) reserve
        self.assertEqual(len(reserve), 3)
        self.assertIn(4, reserve)
        self.assertIn(5, reserve)
        self.assertIn(6, reserve)
        
        # Verify all trees in the reserve are healthy
        for tree_id in reserve:
            self.assertEqual(self.forest_graph.trees[tree_id].health_status, HealthStatus.HEALTHY)
    
    def test_reserve_isolation(self):
        """
        Test that identified reserves are properly isolated from unhealthy trees.
        Verifies that no tree in any reserve is connected to an unhealthy tree.
        """
        # Create a graph with a healthy cluster connected to an unhealthy tree
        graph = ForestGraph()
        graph.add_tree(Tree(1, "Oak", 10, HealthStatus.HEALTHY))
        graph.add_tree(Tree(2, "Pine", 8, HealthStatus.HEALTHY))
        graph.add_tree(Tree(3, "Maple", 12, HealthStatus.HEALTHY))
        graph.add_tree(Tree(4, "Birch", 5, HealthStatus.AT_RISK))
        
        # Create a complete graph among the healthy trees
        t1 = graph.trees[1]
        t2 = graph.trees[2]
        t3 = graph.trees[3]
        t4 = graph.trees[4]
        
        graph.add_path(Path(t1, t2, 10.0))
        graph.add_path(Path(t1, t3, 11.0))
        graph.add_path(Path(t2, t3, 12.0))
        
        # Connect one healthy tree to the at-risk tree
        graph.add_path(Path(t3, t4, 13.0))
        
        # Should not find any reserves
        reserves = find_reserves(graph)
        self.assertEqual(len(reserves), 0, "No reserves should be found if connected to at-risk trees")
    
    def test_reserve_complete_graph(self):
        """
        Test that reserves form complete graphs (fully connected).
        Verifies that every tree in a reserve is connected to all other trees in that reserve.
        """
        # Create a graph with a non-complete healthy cluster
        graph = ForestGraph()
        graph.add_tree(Tree(1, "Oak", 10, HealthStatus.HEALTHY))
        graph.add_tree(Tree(2, "Pine", 8, HealthStatus.HEALTHY))
        graph.add_tree(Tree(3, "Maple", 12, HealthStatus.HEALTHY))
        
        # Get tree objects
        t1 = graph.trees[1]
        t2 = graph.trees[2]
        t3 = graph.trees[3]
        
        # Create a line graph (not complete)
        graph.add_path(Path(t1, t2, 10.0))
        graph.add_path(Path(t2, t3, 12.0))
        # Missing edge: 1-3
        
        # Should not find any reserves
        reserves = find_reserves(graph)
        self.assertEqual(len(reserves), 0, "Non-complete graphs should not be identified as reserves")

    def test_empty_graph(self):
        """
        Test edge case: finding reserves in an empty forest graph.
        Verifies that the function returns an empty list for an empty graph.
        """
        empty_graph = ForestGraph()
        reserves = find_reserves(empty_graph)
        self.assertEqual(len(reserves), 0, "Empty graph should have no reserves")

    def test_small_healthy_clusters(self):
        """
        Test edge case: small healthy clusters that don't qualify as reserves.
        Verifies that groups of 1-2 healthy trees are not marked as reserves.
        """
        # Create a small cluster graph
        small_graph = ForestGraph()
        small_graph.add_tree(Tree(1, "Oak", 10, HealthStatus.HEALTHY))
        small_graph.add_tree(Tree(2, "Pine", 12, HealthStatus.HEALTHY))
        
        # Connect the trees
        t1 = small_graph.trees[1]
        t2 = small_graph.trees[2]
        small_graph.add_path(Path(t1, t2, 5.0))
        
        reserves = find_reserves(small_graph)
        self.assertEqual(len(reserves), 0, "Clusters with fewer than 3 trees should not be reserves")

    def test_multiple_isolated_reserves(self):
        """
        Test scenario: multiple isolated reserves in the same forest.
        Verifies that multiple distinct reserves can be identified independently.
        """
        # Create a graph with two separate complete reserves
        graph = ForestGraph()
        
        # First reserve (trees 1-3)
        graph.add_tree(Tree(1, "Oak", 10, HealthStatus.HEALTHY))
        graph.add_tree(Tree(2, "Pine", 12, HealthStatus.HEALTHY))
        graph.add_tree(Tree(3, "Maple", 15, HealthStatus.HEALTHY))
        
        # Second reserve (trees 4-6)
        graph.add_tree(Tree(4, "Oak", 9, HealthStatus.HEALTHY))
        graph.add_tree(Tree(5, "Pine", 11, HealthStatus.HEALTHY))
        graph.add_tree(Tree(6, "Maple", 13, HealthStatus.HEALTHY))
        
        # Get tree objects
        t1 = graph.trees[1]
        t2 = graph.trees[2]
        t3 = graph.trees[3]
        t4 = graph.trees[4]
        t5 = graph.trees[5]
        t6 = graph.trees[6]
        
        # Connect first reserve as a complete graph
        graph.add_path(Path(t1, t2, 5.0))
        graph.add_path(Path(t1, t3, 6.0))
        graph.add_path(Path(t2, t3, 7.0))
        
        # Connect second reserve as a complete graph
        graph.add_path(Path(t4, t5, 4.0))
        graph.add_path(Path(t4, t6, 5.0))
        graph.add_path(Path(t5, t6, 6.0))
        
        reserves = find_reserves(graph)
        self.assertEqual(len(reserves), 2, "Should identify two separate reserves")
        
        # Check if both expected reserves are found
        found_reserve_1 = False
        found_reserve_2 = False
        
        for reserve in reserves:
            reserve_set = set(reserve)
            if reserve_set == {1, 2, 3}:
                found_reserve_1 = True
            elif reserve_set == {4, 5, 6}:
                found_reserve_2 = True
                
        self.assertTrue(found_reserve_1, "First reserve (1,2,3) not found")
        self.assertTrue(found_reserve_2, "Second reserve (4,5,6) not found")

if __name__ == '__main__':
    unittest.main()
