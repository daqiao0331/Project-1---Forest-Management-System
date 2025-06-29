"""
Tests for the dataset loader module.
"""
import unittest
import os
import sys
import tempfile

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from forest_management_system.io.dataset_loader import load_forest_from_files
from forest_management_system.data_structures.forest_graph import ForestGraph
from forest_management_system.data_structures.health_status import HealthStatus

class TestDatasetLoader(unittest.TestCase):
    """Test cases for the dataset loader module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary files for testing
        self.tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.path_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        
        # Write test data to tree file
        self.tree_file.write("tree_id,species,age,health_status\n")
        self.tree_file.write("1,Oak,100,Healthy\n")
        self.tree_file.write("2,Pine,50,Infected\n")
        self.tree_file.write("3,Maple,75,Healthy\n")
        self.tree_file.close()
        
        # Write test data to path file
        self.path_file.write("tree_1,tree_2,distance\n")
        self.path_file.write("1,2,10\n")
        self.path_file.write("2,3,15\n")
        self.path_file.close()
    
    def tearDown(self):
        """Clean up after tests."""
        os.unlink(self.tree_file.name)
        os.unlink(self.path_file.name)
    
    def test_load_forest_from_files(self):
        """Test loading forest data from files."""
        forest_graph = load_forest_from_files(self.tree_file.name, self.path_file.name)
        
        # Test that the forest graph was created correctly
        self.assertIsInstance(forest_graph, ForestGraph)
        
        # Test that trees were loaded correctly
        self.assertEqual(len(forest_graph.trees), 3)
        self.assertTrue(1 in forest_graph.trees)
        self.assertTrue(2 in forest_graph.trees)
        self.assertTrue(3 in forest_graph.trees)
        
        # Test tree properties
        self.assertEqual(forest_graph.trees[1].species, "Oak")
        self.assertEqual(forest_graph.trees[1].age, 100)
        self.assertEqual(forest_graph.trees[1].health_status, HealthStatus.HEALTHY)
        
        self.assertEqual(forest_graph.trees[2].species, "Pine")
        self.assertEqual(forest_graph.trees[2].age, 50)
        self.assertEqual(forest_graph.trees[2].health_status, HealthStatus.INFECTED)
        
        # Test that paths were loaded correctly
        self.assertEqual(len(forest_graph.paths), 2)
        
        # Test path properties using get_distance method
        self.assertEqual(forest_graph.get_distance(1, 2), 10)
        self.assertEqual(forest_graph.get_distance(2, 3), 15)

if __name__ == '__main__':
    unittest.main() 