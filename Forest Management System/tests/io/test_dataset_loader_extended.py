import unittest
import os
import tempfile
import csv
from unittest.mock import patch, mock_open, MagicMock

from forest_management_system.io.dataset_loader import load_forest_from_files
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.data_structures.forest_graph import ForestGraph

class TestDatasetLoaderExtended(unittest.TestCase):
    """Extended tests for dataset_loader module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for tests
        self.temp_dir = tempfile.gettempdir()
        
        # Mock messagebox module
        self.messagebox_patcher = patch('forest_management_system.io.dataset_loader.messagebox')
        self.mock_messagebox = self.messagebox_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.messagebox_patcher.stop()
    
    def create_temp_csv(self, filename, content):
        """Create a temporary CSV file with the given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in content:
                writer.writerow(row)
        return filepath
    
    def test_load_valid_data(self):
        """Test loading valid tree and path data."""
        # Create valid tree data
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'AT_RISK'],
            [3, 'Maple', 40, 'INFECTED']
        ]
        
        # Create valid path data
        path_data = [
            ['tree_1', 'tree_2', 'distance'],
            [1, 2, 10.5],
            [2, 3, 8.2],
            [1, 3, 15.0]
        ]
        
        # Create temporary files
        tree_file = self.create_temp_csv('valid_trees.csv', tree_data)
        path_file = self.create_temp_csv('valid_paths.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify trees were loaded
            self.assertEqual(len(graph.trees), 3)
            self.assertTrue(1 in graph.trees)
            self.assertTrue(2 in graph.trees)
            self.assertTrue(3 in graph.trees)
            
            # Verify tree properties
            self.assertEqual(graph.trees[1].species, 'Oak')
            self.assertEqual(graph.trees[2].species, 'Pine')
            self.assertEqual(graph.trees[3].species, 'Maple')
            
            self.assertEqual(graph.trees[1].health_status, HealthStatus.HEALTHY)
            self.assertEqual(graph.trees[2].health_status, HealthStatus.AT_RISK)
            self.assertEqual(graph.trees[3].health_status, HealthStatus.INFECTED)
            
            # Verify paths were loaded
            self.assertEqual(len(graph.adj_list), 3)
            self.assertEqual(len(graph.adj_list[1]), 2)  # Connected to 2 and 3
            self.assertEqual(len(graph.adj_list[2]), 2)  # Connected to 1 and 3
            self.assertEqual(len(graph.adj_list[3]), 2)  # Connected to 1 and 2
            
            # Verify weights
            self.assertAlmostEqual(graph.adj_list[1][2], 10.5)
            self.assertAlmostEqual(graph.adj_list[2][3], 8.2)
            self.assertAlmostEqual(graph.adj_list[1][3], 15.0)
            
            # Verify info message was shown
            self.mock_messagebox.showinfo.assert_called_once()
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)
    
    def test_missing_tree_file(self):
        """Test handling of missing tree file."""
        with self.assertRaises(FileNotFoundError):
            load_forest_from_files('nonexistent_trees.csv', 'nonexistent_paths.csv')
    
    def test_missing_tree_columns(self):
        """Test handling of missing columns in tree file."""
        # Create tree data with missing columns
        tree_data = [
            ['tree_id', 'species', 'age'],  # Missing health_status
            [1, 'Oak', 50],
            [2, 'Pine', 30]
        ]
        
        # Create temporary file
        tree_file = self.create_temp_csv('missing_columns.csv', tree_data)
        path_file = 'dummy_path.csv'  # Won't be used
        
        try:
            with self.assertRaises(ValueError) as context:
                load_forest_from_files(tree_file, path_file)
            
            self.assertIn('Missing required columns', str(context.exception))
            self.assertIn('health_status', str(context.exception))
            
        finally:
            os.remove(tree_file)
    
    def test_invalid_tree_data(self):
        """Test handling of invalid tree data."""
        # Create tree data with various issues
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            ['not_a_number', 'Pine', 30, 'AT_RISK'],  # Invalid tree_id
            [3, 'Maple', 'not_a_number', 'INFECTED'],  # Invalid age
            [4, 'Cedar', 20, 'UNKNOWN'],  # Invalid health status
            [1, 'Duplicate', 60, 'HEALTHY']  # Duplicate tree_id
        ]
        
        # Create path data
        path_data = [['tree_1', 'tree_2', 'distance']]
        
        # Create temporary files
        tree_file = self.create_temp_csv('invalid_trees.csv', tree_data)
        path_file = self.create_temp_csv('empty_paths.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify valid trees were loaded
            self.assertEqual(len(graph.trees), 1)  # Only tree_id 1 (overwritten with duplicate)
            self.assertTrue(1 in graph.trees)
            
            # Verify warning was shown
            self.mock_messagebox.showwarning.assert_called_once()
            warning_args = self.mock_messagebox.showwarning.call_args[0]
            self.assertIn('duplicate tree IDs', warning_args[1])
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)
    
    def test_invalid_path_data(self):
        """Test handling of invalid path data."""
        # Create tree data
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'AT_RISK']
        ]
        
        # Create path data with various issues
        path_data = [
            ['tree_1', 'tree_2', 'distance'],
            [1, 2, 10.5],  # Valid
            ['a', 2, 5.0],  # Invalid tree_id
            [1, 1, 0.0],  # Self-loop
            [1, 3, 7.5],  # Non-existent tree
            [1, 2, -5.0]   # Negative distance
        ]
        
        # Create temporary files
        tree_file = self.create_temp_csv('valid_trees.csv', tree_data)
        path_file = self.create_temp_csv('invalid_paths.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify trees were loaded
            self.assertEqual(len(graph.trees), 2)
            
            # Verify only valid path was loaded
            self.assertEqual(len(graph.adj_list), 2)
            self.assertEqual(len(graph.adj_list[1]), 1)  # Connected only to 2
            self.assertEqual(len(graph.adj_list[2]), 1)  # Connected only to 1
            self.assertAlmostEqual(graph.adj_list[1][2], 10.5)
            
            # Verify warning was shown
            self.mock_messagebox.showwarning.assert_called_once()
            warning_args = self.mock_messagebox.showwarning.call_args[0]
            self.assertIn('paths could not be loaded', warning_args[1])
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)
    
    def test_missing_path_file(self):
        """Test handling of missing path file."""
        # Create tree data
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'AT_RISK']
        ]
        
        # Create temporary file
        tree_file = self.create_temp_csv('valid_trees.csv', tree_data)
        
        try:
            # Test loading the data with non-existent path file
            graph = load_forest_from_files(tree_file, 'nonexistent_paths.csv')
            
            # Verify trees were loaded
            self.assertEqual(len(graph.trees), 2)
            
            # Verify no paths were loaded
            self.assertEqual(len(graph.adj_list), 2)
            self.assertEqual(len(graph.adj_list[1]), 0)
            self.assertEqual(len(graph.adj_list[2]), 0)
            
            # Verify warning was shown
            self.mock_messagebox.showwarning.assert_called_once()
            warning_args = self.mock_messagebox.showwarning.call_args[0]
            self.assertIn('Path file not found', warning_args[1])
            
        finally:
            # Clean up temporary file
            os.remove(tree_file)
    
    def test_missing_path_columns(self):
        """Test handling of missing columns in path file."""
        # Create tree data
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'AT_RISK']
        ]
        
        # Create path data with missing column
        path_data = [
            ['tree_1', 'tree_2'],  # Missing distance
            [1, 2]
        ]
        
        # Create temporary files
        tree_file = self.create_temp_csv('valid_trees.csv', tree_data)
        path_file = self.create_temp_csv('missing_path_columns.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify trees were loaded but no paths
            self.assertEqual(len(graph.trees), 2)
            self.assertEqual(len(graph.adj_list), 2)
            self.assertEqual(len(graph.adj_list[1]), 0)
            
            # Verify warning was shown
            self.mock_messagebox.showwarning.assert_called_once()
            warning_args = self.mock_messagebox.showwarning.call_args[0]
            self.assertIn('Missing required columns in path file', warning_args[1])
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)
    
    def test_empty_tree_file(self):
        """Test handling of empty tree file."""
        # Create empty tree data (header only)
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status']
        ]
        
        # Create empty path data (header only)
        path_data = [
            ['tree_1', 'tree_2', 'distance']
        ]
        
        # Create temporary files
        tree_file = self.create_temp_csv('empty_trees.csv', tree_data)
        path_file = self.create_temp_csv('empty_paths.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify no trees were loaded
            self.assertEqual(len(graph.trees), 0)
            self.assertEqual(len(graph.adj_list), 0)
            
            # Verify error was shown
            self.mock_messagebox.showerror.assert_called_once()
            error_args = self.mock_messagebox.showerror.call_args[0]
            self.assertIn('No valid trees found', error_args[1])
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)

    def test_alternative_column_names(self):
        """Test loading with alternative column names for paths."""
        # Create tree data
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'AT_RISK']
        ]
        
        # Create path data with alternative column names
        path_data = [
            ['tree_id1', 'tree_id2', 'distance'],  # Using tree_id1/tree_id2 instead of tree_1/tree_2
            [1, 2, 10.5]
        ]
        
        # Create temporary files
        tree_file = self.create_temp_csv('valid_trees.csv', tree_data)
        path_file = self.create_temp_csv('alt_paths.csv', path_data)
        
        try:
            # Test loading the data
            graph = load_forest_from_files(tree_file, path_file)
            
            # Verify trees and paths were loaded
            self.assertEqual(len(graph.trees), 2)
            self.assertEqual(len(graph.adj_list), 2)
            self.assertEqual(len(graph.adj_list[1]), 1)
            self.assertAlmostEqual(graph.adj_list[1][2], 10.5)
            
            # Verify info message was shown
            self.mock_messagebox.showinfo.assert_called_once()
            
        finally:
            # Clean up temporary files
            os.remove(tree_file)
            os.remove(path_file)
    
    def test_health_status_formats(self):
        """Test handling various health status formats."""
        # Create tree data with different health status formats
        tree_data = [
            ['tree_id', 'species', 'age', 'health_status'],
            [1, 'Oak', 50, 'HEALTHY'],
            [2, 'Pine', 30, 'at_risk'],  # lowercase
            [3, 'Maple', 40, 'Infected'],  # Mixed case
            [4, 'Birch', 25, 'AT RISK']   # With space
        ]
        
        # Create temporary file
        tree_file = self.create_temp_csv('health_status_trees.csv', tree_data)
        path_file = 'dummy_path.csv'  # Won't be used
        
        try:
            # Test loading the data
            with patch('forest_management_system.io.dataset_loader.open', mock_open()) as mock_file:
                # Mock path file to avoid FileNotFoundError
                mock_file.side_effect = [open(tree_file, 'r', encoding='utf-8'), FileNotFoundError]
                
                graph = load_forest_from_files(tree_file, path_file)
                
                # Verify trees were loaded
                self.assertEqual(len(graph.trees), 4)
                self.assertEqual(graph.trees[1].health_status, HealthStatus.HEALTHY)
                self.assertEqual(graph.trees[2].health_status, HealthStatus.AT_RISK)
                self.assertEqual(graph.trees[3].health_status, HealthStatus.INFECTED)
                self.assertEqual(graph.trees[4].health_status, HealthStatus.AT_RISK)
                
                # Verify warning about missing path file was shown
                self.mock_messagebox.showwarning.assert_called_once()
                
        finally:
            # Clean up temporary file
            os.remove(tree_file)

if __name__ == '__main__':
    unittest.main() 