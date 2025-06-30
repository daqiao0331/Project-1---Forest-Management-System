"""
Tests for the dataset loader module.
"""
import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, ANY

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from forest_management_system.io.dataset_loader import load_forest_from_files
from forest_management_system.data_structures.forest_graph import ForestGraph
from forest_management_system.data_structures.health_status import HealthStatus

class TestDatasetLoader(unittest.TestCase):
    """Test cases for the dataset loader module."""
    
    def setUp(self):
        """
        Set up test environment with temporary files containing test data.
        Creates two temp files: one for trees and one for paths.
        """
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
        
        # Mock the messagebox to avoid UI dialogs during tests
        self.patcher = patch('forest_management_system.io.dataset_loader.messagebox')
        self.mock_messagebox = self.patcher.start()
    
    def tearDown(self):
        """
        Clean up after tests by removing temporary files and stopping patches.
        Ensures a clean environment for the next test.
        """
        os.unlink(self.tree_file.name)
        os.unlink(self.path_file.name)
        self.patcher.stop()
        
        # Clean up any temp files created in the tests
        for attr_name in dir(self):
            if attr_name.endswith('_file') and hasattr(self, attr_name) and hasattr(getattr(self, attr_name), 'name'):
                try:
                    os.unlink(getattr(self, attr_name).name)
                except (OSError, FileNotFoundError):
                    pass
    
    def test_load_forest_from_files(self):
        """
        Test basic functionality of loading forest data from valid files.
        Verifies trees, their properties, and paths are loaded correctly.
        """
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
        
        # Test if paths are loaded correctly - using adjacency list
        # Calculate the number of loaded paths
        path_count = 0
        for tree_id, neighbors in forest_graph.adj_list.items():
            path_count += len(neighbors)
        # Because undirected graphs, each path appears twice in adjacency list, so divide by 2
        self.assertEqual(path_count // 2, 2)
        
        # Test path properties using get_distance method
        self.assertEqual(forest_graph.get_distance(1, 2), 10)
        self.assertEqual(forest_graph.get_distance(2, 3), 15)
        
        # Verify info message was shown
        self.mock_messagebox.showinfo.assert_called_with(
            "Data Loading Complete", 
            ANY
        )

    def test_missing_tree_file(self):
        """
        Test error handling when tree file is missing.
        Verifies that appropriate FileNotFoundError is raised.
        """
        with self.assertRaises(FileNotFoundError):
            load_forest_from_files('nonexistent_file.csv', self.path_file.name)

    def test_missing_path_file(self):
        """
        Test error handling when path file is missing.
        Verifies that a warning is shown but the function still returns a graph with trees.
        """
        forest_graph = load_forest_from_files(self.tree_file.name, 'nonexistent_file.csv')
        
        # Check if the trees were still loaded
        self.assertEqual(len(forest_graph.trees), 3)
        
        # Verify warning message was shown for missing path file
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that the warning contains "Path file not found"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("Path file not found", warning_msg)

    def test_invalid_column_names(self):
        """
        Test handling of invalid column names in CSV files.
        Verifies appropriate error message when required columns are missing.
        """
        # Create tree file with invalid column names
        invalid_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        invalid_tree_file.write("id,type,years,condition\n")  # Wrong column names
        invalid_tree_file.write("1,Oak,100,Healthy\n")
        invalid_tree_file.close()
        
        # Test with mock to avoid UI dialogs
        with self.assertRaises(ValueError) as context:
            load_forest_from_files(invalid_tree_file.name, self.path_file.name)
        
        # Check error message contains missing columns
        self.assertIn("Missing required columns", str(context.exception))
        
        # Clean up
        os.unlink(invalid_tree_file.name)

    def test_missing_columns(self):
        """
        Test loading data with missing required columns.
        Verifies appropriate error message when required columns are missing.
        """
        # Create tree file with missing column
        missing_col_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        # Missing the health_status column
        missing_col_tree_file.write("tree_id,species,age\n")
        missing_col_tree_file.write("1,Oak,100\n")
        missing_col_tree_file.close()
        
        # Should raise ValueError due to missing column
        with self.assertRaises(ValueError) as context:
            load_forest_from_files(missing_col_tree_file.name, self.path_file.name)
        
        # Check error message
        self.assertIn("Missing required columns", str(context.exception))
        
        # Path file with missing columns
        normal_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        normal_tree_file.write("tree_id,species,age,health_status\n")
        normal_tree_file.write("1,Oak,100,Healthy\n")
        normal_tree_file.close()
        
        missing_col_path_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        # Missing distance column
        missing_col_path_file.write("tree_1,tree_2\n")
        missing_col_path_file.write("1,2\n")
        missing_col_path_file.close()
        
        # Should warn about missing column in path file but not raise error
        forest_graph = load_forest_from_files(normal_tree_file.name, missing_col_path_file.name)
        
        # Check that warning was shown
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Verify that the warning message mentions missing columns
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("Missing required columns", warning_msg)
        
        # Clean up
        os.unlink(missing_col_tree_file.name)
        os.unlink(normal_tree_file.name)
        os.unlink(missing_col_path_file.name)

    def test_duplicate_tree_ids(self):
        """
        Test handling of duplicate tree IDs in input file.
        Verifies newer entries overwrite older ones and warning is shown.
        """
        # Create tree file with duplicate IDs
        dup_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        dup_tree_file.write("tree_id,species,age,health_status\n")
        dup_tree_file.write("1,Oak,100,Healthy\n")
        dup_tree_file.write("2,Pine,50,Infected\n")
        dup_tree_file.write("1,Maple,75,At_Risk\n")  # Duplicate ID
        dup_tree_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(dup_tree_file.name, self.path_file.name)
        
        # Check that newer entries overwrote older ones
        self.assertEqual(forest_graph.trees[1].species, "Maple")
        self.assertEqual(forest_graph.trees[1].age, 75)
        self.assertEqual(forest_graph.trees[1].health_status, HealthStatus.AT_RISK)
        
        # Verify warning message was shown
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that warning contains "duplicate tree IDs"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("duplicate tree IDs", warning_msg)
        
        # Clean up
        os.unlink(dup_tree_file.name)

    def test_invalid_health_status(self):
        """
        Test handling of invalid health status values.
        Verifies error tracking for invalid health status values.
        """
        # Create tree file with invalid health status
        invalid_health_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        invalid_health_file.write("tree_id,species,age,health_status\n")
        invalid_health_file.write("1,Oak,100,Healthy\n")
        invalid_health_file.write("2,Pine,50,Invalid_Status\n")  # Invalid health status
        invalid_health_file.write("3,Maple,75,Healthy\n")
        invalid_health_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(invalid_health_file.name, self.path_file.name)
        
        # Check that valid trees were loaded
        self.assertEqual(len(forest_graph.trees), 2)  # Only 2 valid trees
        self.assertTrue(1 in forest_graph.trees)
        self.assertTrue(3 in forest_graph.trees)
        self.assertFalse(2 in forest_graph.trees)
        
        # Verify warning message was shown
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that warning contains "could not be loaded"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("could not be loaded", warning_msg)
        
        # Clean up
        os.unlink(invalid_health_file.name)

    def test_invalid_numeric_values(self):
        """
        Test handling of invalid numeric values (age, tree_id).
        Verifies error tracking for non-numeric values in numeric fields.
        """
        # Create tree file with invalid numeric values
        invalid_num_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        invalid_num_file.write("tree_id,species,age,health_status\n")
        invalid_num_file.write("1,Oak,100,Healthy\n")
        invalid_num_file.write("abc,Pine,50,Infected\n")  # Invalid tree_id
        invalid_num_file.write("3,Maple,unknown,Healthy\n")  # Invalid age
        invalid_num_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(invalid_num_file.name, self.path_file.name)
        
        # Check that only valid trees were loaded
        self.assertEqual(len(forest_graph.trees), 1)  # Only 1 valid tree
        self.assertTrue(1 in forest_graph.trees)
        
        # Verify warning message was shown for data loading issues
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that warning contains "could not be loaded"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("could not be loaded", warning_msg)
        
        # Clean up
        os.unlink(invalid_num_file.name)

    def test_invalid_paths(self):
        """
        Test handling of invalid paths (non-existent tree IDs, negative distances).
        Verifies error tracking for invalid path entries.
        """
        # Create path file with invalid paths
        invalid_path_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        invalid_path_file.write("tree_1,tree_2,distance\n")
        invalid_path_file.write("1,2,10\n")  # Valid
        invalid_path_file.write("1,4,-5\n")  # Negative distance & non-existent tree
        invalid_path_file.write("1,1,5\n")  # Self-loop
        invalid_path_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(self.tree_file.name, invalid_path_file.name)
        
        # Check that only valid paths were loaded
        path_count = 0
        for tree_id, neighbors in forest_graph.adj_list.items():
            path_count += len(neighbors)
        self.assertEqual(path_count // 2, 1)  # Only 1 valid path
        
        # Verify warning message was shown for path loading issues
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that warning contains "paths could not be loaded"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("paths could not be loaded", warning_msg)
        
        # Clean up
        os.unlink(invalid_path_file.name)

    def test_empty_tree_file(self):
        """
        Test handling of empty tree files (with header only).
        Verifies appropriate warning/error messages for empty data.
        """
        # Create empty tree file (with header only)
        empty_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        empty_tree_file.write("tree_id,species,age,health_status\n")
        empty_tree_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(empty_tree_file.name, self.path_file.name)
        
        # Check that no trees were loaded
        self.assertEqual(len(forest_graph.trees), 0)
        
        # Verify error message was shown
        self.mock_messagebox.showerror.assert_called_with(
            "Data Loading Errors", 
            ANY
        )
        # Check that error message contains "No valid trees found"
        error_msg = self.mock_messagebox.showerror.call_args[0][1]
        self.assertIn("No valid trees found", error_msg)
        
        # Clean up
        os.unlink(empty_tree_file.name)

    def test_empty_files(self):
        """
        Test loading completely empty files.
        Verifies appropriate error messages for empty files.
        """
        # Create empty files (no content, not even headers)
        completely_empty_tree_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        completely_empty_tree_file.write("")  # Completely empty file
        completely_empty_tree_file.close()
        
        completely_empty_path_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        completely_empty_path_file.write("")  # Completely empty file
        completely_empty_path_file.close()
        
        # Load forest with empty tree file
        with self.assertRaises(ValueError):
            load_forest_from_files(completely_empty_tree_file.name, self.path_file.name)
        
        # Try with valid tree file but empty path file
        forest_graph = load_forest_from_files(self.tree_file.name, completely_empty_path_file.name)
        
        # Should still load trees but no paths
        self.assertEqual(len(forest_graph.trees), 3)
        path_count = 0
        for tree_id, neighbors in forest_graph.adj_list.items():
            path_count += len(neighbors)
        self.assertEqual(path_count, 0)  # No paths loaded
        
        # Verify warning message was shown
        self.mock_messagebox.showwarning.assert_called_with(
            "Data Loading Warnings", 
            ANY
        )
        # Check that warning contains "Error reading path file"
        warning_msg = self.mock_messagebox.showwarning.call_args[0][1]
        self.assertIn("Error reading path file", warning_msg)
        
        # Clean up
        os.unlink(completely_empty_tree_file.name)
        os.unlink(completely_empty_path_file.name)

    def test_alternative_path_column_names(self):
        """
        Test support for alternative path column naming (tree_id1/tree_id2).
        Verifies loader can handle different column naming conventions.
        """
        # Create path file with alternative column names
        alt_path_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        alt_path_file.write("tree_id1,tree_id2,distance\n")  # Alternative column names
        alt_path_file.write("1,2,10\n")
        alt_path_file.write("2,3,15\n")
        alt_path_file.close()
        
        # Load the forest
        forest_graph = load_forest_from_files(self.tree_file.name, alt_path_file.name)
        
        # Check that paths were loaded correctly
        self.assertEqual(forest_graph.get_distance(1, 2), 10)
        self.assertEqual(forest_graph.get_distance(2, 3), 15)
        
        # Verify info message was shown
        self.mock_messagebox.showinfo.assert_called_with(
            "Data Loading Complete", 
            ANY
        )
        
        # Clean up
        os.unlink(alt_path_file.name)

if __name__ == '__main__':
    unittest.main() 