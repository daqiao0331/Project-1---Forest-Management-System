import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from forest_management_system.data_structures.tree import Tree
from forest_management_system.data_structures.health_status import HealthStatus
from forest_management_system.data_structures.path import Path

class TestPath(unittest.TestCase):
    def setUp(self):
        """
        Set up common Tree objects used across multiple test cases.
        Creates trees with different properties for testing Path instances.
        """
        self.t1 = Tree(1, 'Oak', 10, HealthStatus.HEALTHY)
        self.t2 = Tree(2, 'Pine', 8, HealthStatus.INFECTED)
        self.t3 = Tree(3, 'Maple', 15, HealthStatus.AT_RISK)
        self.t4 = Tree(1, 'Oak', 20, HealthStatus.HEALTHY)  # Same ID as t1

    def test_path_init(self):
        """
        Test the initialization of Path objects with valid parameters.
        Verifies all attributes are correctly assigned during instantiation.
        """
        # Basic initialization
        p = Path(self.t1, self.t2, 5.0)
        self.assertEqual(p.tree1, self.t1)
        self.assertEqual(p.tree2, self.t2)
        self.assertEqual(p.weight, 5.0)
        
        # Test with zero distance (edge case)
        p_zero = Path(self.t1, self.t3, 0.0)
        self.assertEqual(p_zero.weight, 0.0)
        
        # Test with negative distance (edge case)
        p_negative = Path(self.t2, self.t3, -1.5)
        self.assertEqual(p_negative.weight, -1.5)
        
        # Test with same tree at both ends (edge case)
        p_same = Path(self.t1, self.t1, 0.0)
        self.assertEqual(p_same.tree1, p_same.tree2)
        
        # Test with trees having same ID but different properties
        p_same_id = Path(self.t1, self.t4, 3.0)
        self.assertEqual(p_same_id.tree1.tree_id, p_same_id.tree2.tree_id)

    def test_path_validation(self):
        """
        Test validation during Path initialization.
        Verifies appropriate errors are raised for invalid inputs.
        """
        # Test with non-Tree objects
        with self.assertRaises(ValueError):
            Path("not a tree", self.t2, 5.0)
            
        with self.assertRaises(ValueError):
            Path(self.t1, "not a tree", 5.0)
            
        with self.assertRaises(ValueError):
            Path("tree1", "tree2", 5.0)
        
        # Test with None values
        with self.assertRaises(ValueError):
            Path(None, self.t2, 5.0)
            
        with self.assertRaises(ValueError):
            Path(self.t1, None, 5.0)

    def test_path_equality(self):
        """
        Test equality comparison of Path objects.
        Verifies that Path equality is bidirectional and considers weight.
        """
        # Basic equality test (path direction doesn't matter)
        p1 = Path(self.t1, self.t2, 5.0)
        p2 = Path(self.t2, self.t1, 5.0)
        self.assertEqual(p1, p2)
        
        # Test with same trees but different weight
        p3 = Path(self.t1, self.t2, 10.0)
        self.assertNotEqual(p1, p3)
        
        # Test with different trees but same weight
        p4 = Path(self.t1, self.t3, 5.0)
        self.assertNotEqual(p1, p4)
        
        # Test with non-Path object
        self.assertFalse(p1 == "Not a path")
        
        # Test reflexive property
        self.assertEqual(p1, p1)
        
        # Test with trees having the same IDs
        p5 = Path(self.t1, self.t4, 5.0)  # t1 and t4 have same ID
        p6 = Path(self.t4, self.t1, 5.0)
        self.assertEqual(p5, p6)

    def test_path_repr(self):
        """
        Test string representation of Path objects.
        Verifies that the repr contains essential path information.
        """
        p = Path(self.t1, self.t2, 5.0)
        s = repr(p)
        self.assertIn('Path', s)
        self.assertIn('distance', s)
        self.assertIn(str(self.t1.tree_id), s)
        self.assertIn(str(self.t2.tree_id), s)
        self.assertIn(str(p.weight), s)
        
        # Test with special values
        p_zero = Path(self.t1, self.t3, 0.0)
        self.assertIn('0.0', repr(p_zero))
        
        # Test with negative weight
        p_neg = Path(self.t2, self.t3, -3.5)
        self.assertIn('-3.5', repr(p_neg))
        
        # Test with very large weight (edge case)
        p_large = Path(self.t1, self.t2, 1e10)
        self.assertIn(str(1e10), repr(p_large))

if __name__ == '__main__':
    unittest.main()
