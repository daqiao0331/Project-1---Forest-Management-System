import unittest
from project_name.tree import Tree

class TestTree(unittest.TestCase):
    def test_tree_init(self):
        tree = Tree('Oak', 8, 'Healthy', 'ForestA')
        self.assertEqual(tree.species, 'Oak')
        self.assertEqual(tree.age, 8)
        self.assertEqual(tree.health, 'Healthy')
        self.assertEqual(tree.forest, 'ForestA')

if __name__ == '__main__':
    unittest.main()
