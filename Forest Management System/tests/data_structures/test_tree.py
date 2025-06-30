import unittest
import sys
import os
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus

class TestTree(unittest.TestCase):
    def test_tree_init(self):
        """
        Test the initialization of Tree objects with valid parameters.
        Verifies all attributes are correctly assigned during instantiation.
        """
        tree = Tree(1, 'Oak', 8, HealthStatus.HEALTHY, 'ForestA')
        self.assertEqual(tree.tree_id, 1)
        self.assertEqual(tree.species, 'Oak')
        self.assertEqual(tree.age, 8)
        self.assertEqual(tree.health_status, HealthStatus.HEALTHY)
        self.assertEqual(tree.forest, 'ForestA')
        
        # Test with None forest (edge case)
        tree_no_forest = Tree(2, 'Pine', 10, HealthStatus.AT_RISK)
        self.assertIsNone(tree_no_forest.forest)
        
        # Test with integer ID at boundary
        tree_max_id = Tree(2147483647, 'Maple', 15, HealthStatus.INFECTED)
        self.assertEqual(tree_max_id.tree_id, 2147483647)
        
        # Test with zero age (edge case)
        tree_zero_age = Tree(3, 'Birch', 0, HealthStatus.HEALTHY)
        self.assertEqual(tree_zero_age.age, 0)

    def test_health_status_enum(self):
        """
        Test error handling when invalid health status is provided.
        Verifies that appropriate ValueError is raised for non-enum values.
        """
        # Test with invalid string that can't be converted to health status
        with self.assertRaises(ValueError):
            Tree(2, 'Pine', 5, 'not_enum')
            
        # Test with invalid type (dict)
        with self.assertRaises(ValueError):
            Tree(3, 'Oak', 8, {'status': 'healthy'})
            
        # Test with None value
        with self.assertRaises(ValueError):
            Tree(4, 'Birch', 12, None)

    def test_health_status_string_conversion(self):
        """
        Test the conversion of string values to HealthStatus enum.
        Verifies both uppercase and lowercase string conversion works correctly.
        """
        # Test lowercase string conversion
        tree1 = Tree(1, 'Oak', 8, 'healthy')
        self.assertEqual(tree1.health_status, HealthStatus.HEALTHY)
        
        # Test uppercase string conversion
        tree2 = Tree(2, 'Pine', 5, 'INFECTED')
        self.assertEqual(tree2.health_status, HealthStatus.INFECTED)
        
        # Test mixed case string conversion
        tree3 = Tree(3, 'Maple', 10, 'At_Risk')
        self.assertEqual(tree3.health_status, HealthStatus.AT_RISK)

    def test_repr_and_eq(self):
        """
        Test string representation and equality comparison of Tree objects.
        Verifies repr contains essential info and equality is based on tree_id.
        """
        t1 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t2 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t3 = Tree(2, 'Pine', 5, HealthStatus.INFECTED)
        
        # Test equality based on ID
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        
        # Test repr contains essential information
        repr_str = repr(t1)
        self.assertIn('Tree', repr_str)
        self.assertIn('id=1', repr_str)
        self.assertIn('species=Oak', repr_str)
        
        # Test equality with same ID but different attributes (edge case)
        t4 = Tree(1, 'Maple', 20, HealthStatus.INFECTED)  # Same ID as t1 but different attributes
        self.assertEqual(t1, t4)  # Should be equal because only ID matters
        
        # Test equality with non-Tree object (edge case)
        self.assertFalse(t1 == "Not a Tree")

    def test_lt(self):
        """
        Test the less than comparison operator for Tree objects.
        Verifies comparison is based on tree_id attribute.
        """
        t1 = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        t2 = Tree(2, 'Pine', 5, HealthStatus.INFECTED)
        t3 = Tree(3, 'Maple', 10, HealthStatus.AT_RISK)
        
        # Test basic less than comparison
        self.assertTrue(t1 < t2)
        self.assertTrue(t2 < t3)
        self.assertTrue(t1 < t3)
        
        # Test not less than
        self.assertFalse(t2 < t1)
        self.assertFalse(t3 < t1)
        
        # Test equality case (edge case)
        t4 = Tree(1, 'Different', 100, HealthStatus.INFECTED)
        self.assertFalse(t1 < t4)
        self.assertFalse(t4 < t1)

    def test_health_status_setter(self):
        """
        Test the health_status property setter.
        Verifies that health status can be updated after initialization.
        """
        tree = Tree(1, 'Oak', 8, HealthStatus.HEALTHY)
        self.assertEqual(tree.health_status, HealthStatus.HEALTHY)
        
        # Change health status with enum
        tree.health_status = HealthStatus.INFECTED
        self.assertEqual(tree.health_status, HealthStatus.INFECTED)
        
        # Change health status with string
        tree.health_status = 'at_risk'
        self.assertEqual(tree.health_status, HealthStatus.AT_RISK)
        
        # Test with invalid status
        with self.assertRaises(ValueError):
            tree.health_status = 'invalid_status'

    def test_edge_case_inputs(self):
        """
        Test edge cases for Tree initialization.
        Tests boundary values and unusual inputs for robustness.
        """
        # Test with negative age (edge case)
        tree_negative_age = Tree(5, 'Oak', -1, HealthStatus.HEALTHY)
        self.assertEqual(tree_negative_age.age, -1)
        
        # Test with empty species string (edge case)
        tree_empty_species = Tree(6, '', 10, HealthStatus.HEALTHY)
        self.assertEqual(tree_empty_species.species, '')
        
        # Test with very long species name (edge case)
        long_species = 'A' * 1000
        tree_long_species = Tree(7, long_species, 10, HealthStatus.HEALTHY)
        self.assertEqual(tree_long_species.species, long_species)

if __name__ == '__main__':
    unittest.main()
