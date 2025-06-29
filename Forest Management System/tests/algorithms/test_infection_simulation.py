import unittest
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.io.dataset_loader import load_forest_from_files
from forest_management_system.algorithms.infection_simulation import simulate_infection
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.path import Path
from forest_management_system.data_structures.forest_graph import ForestGraph

class TestInfectionSimulation(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        trees_file = os.path.join(base_dir, 'data', 'forest_management_dataset-trees.csv')
        paths_file = os.path.join(base_dir, 'data', 'forest_management_dataset-paths.csv')
        try:
            self.graph = load_forest_from_files(trees_file, paths_file)
        except FileNotFoundError:
            # Create a simple test graph if data files don't exist
            self.graph = self.create_test_graph()

    def create_test_graph(self):
        """Create a test graph for testing when CSV files aren't available."""
        graph = ForestGraph()
        # Create trees with different health statuses
        trees = [
            Tree(1, "Pine", 10, HealthStatus.HEALTHY),
            Tree(2, "Oak", 15, HealthStatus.INFECTED),  # Infected tree
            Tree(3, "Maple", 8, HealthStatus.HEALTHY),
            Tree(4, "Pine", 12, HealthStatus.AT_RISK),
            Tree(5, "Oak", 20, HealthStatus.HEALTHY),
            Tree(6, "Birch", 5, HealthStatus.INFECTED)  # Another infected tree
        ]
        
        # Add trees to graph
        for tree in trees:
            graph.add_tree(tree)
            
        # Connect trees
        paths = [
            Path(trees[0], trees[1], 10.0),  # 1-2
            Path(trees[1], trees[2], 5.0),   # 2-3
            Path(trees[2], trees[3], 8.0),   # 3-4
            Path(trees[0], trees[3], 15.0),  # 1-4
            Path(trees[3], trees[4], 12.0),  # 4-5
            # Tree 6 is isolated
        ]
        
        for path in paths:
            graph.add_path(path)
            
        return graph

    def test_simulate_infection(self):
        """Test basic infection simulation from an infected tree."""
        # Find an infected tree as the start
        start = next((tid for tid, t in self.graph.trees.items() 
                     if t.health_status == HealthStatus.INFECTED), None)
        
        if start is None:
            self.skipTest("No infected tree found in the graph for testing.")
            
        # Run simulation
        infection_results = simulate_infection(self.graph, start)
        
        # Extract tree IDs and infection times
        infected_ids = [item[0] for item in infection_results]
        infection_times = {item[0]: item[2] for item in infection_results}
        
        # Verify simulation results
        self.assertIn(start, infected_ids, "Starting tree should be in results")
        self.assertEqual(infection_times[start], 0, "Start tree should have infection time 0")
        
        # Verify all infected trees are valid trees in the graph
        for tid in infected_ids:
            self.assertIn(tid, self.graph.trees, f"Tree {tid} not in graph")
            
        # Check infection ordering - trees further away should be infected later
        for tid, parent_id, time in infection_results[1:]:  # Skip the first one
            if parent_id is not None:
                self.assertGreater(time, infection_times[parent_id], 
                    f"Tree {tid} should be infected after its parent {parent_id}")
    
    def test_simulate_infection_from_healthy_tree(self):
        """Test that simulation doesn't work when starting from a healthy tree."""
        # Find a healthy tree
        healthy_id = next((tid for tid, t in self.graph.trees.items()
                          if t.health_status == HealthStatus.HEALTHY), None)
        
        if healthy_id is None:
            self.skipTest("No healthy tree found in the graph for testing.")
        
        # Simulation should return empty list when starting from healthy tree
        result = simulate_infection(self.graph, healthy_id)
        self.assertEqual(result, [], 
                        "Simulation from healthy tree should return empty list")
    
    def test_infection_path_distances(self):
        """Test that infection times are proportional to path distances."""
        # Create a controlled test graph
        graph = ForestGraph()
        trees = [
            Tree(1, "Pine", 10, HealthStatus.INFECTED),  # Infected tree as start
            Tree(2, "Oak", 15, HealthStatus.HEALTHY),    # Close to start (dist=5)
            Tree(3, "Maple", 8, HealthStatus.HEALTHY),   # Far from start (dist=20)
        ]
        
        for tree in trees:
            graph.add_tree(tree)
            
        # Add paths with known distances
        graph.add_path(Path(trees[0], trees[1], 5.0))   # Short distance
        graph.add_path(Path(trees[1], trees[2], 15.0))  # Longer distance
        
        # Run simulation
        infection_results = simulate_infection(graph, 1)
        
        # Extract infection times
        times = {item[0]: item[2] for item in infection_results}
        
        self.assertEqual(times[1], 0, "Start tree should have time 0")
        self.assertLess(times[2], times[3], 
                       "Tree 2 (closer) should be infected before Tree 3 (farther)")
        
    def test_simulate_infection_with_isolated_tree(self):
        """Test that isolated trees don't get infected."""
        graph = self.create_test_graph()
        
        # Tree 6 is isolated and infected
        result = simulate_infection(graph, 6)
        
        # Should only include the isolated tree itself
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 6)
        
    def test_simulation_with_invalid_tree_id(self):
        """Test simulation with a non-existent tree ID."""
        invalid_id = max(self.graph.trees.keys()) + 1000  # Ensure it's invalid
        result = simulate_infection(self.graph, invalid_id)
        self.assertEqual(result, [], "Simulation with invalid tree ID should return empty list")

if __name__ == '__main__':
    unittest.main()
