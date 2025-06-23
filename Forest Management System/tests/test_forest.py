import unittest
from project_name.forest import Forest
from project_name.tree import Tree

class TestForest(unittest.TestCase):
    def setUp(self):
        self.forest = Forest('TestForest', 'TestLocation', 100)
        self.tree = Tree('Pine', 5, 'Healthy', self.forest.name)

    def test_add_tree(self):
        self.forest.add_tree(self.tree)
        self.assertEqual(self.forest.get_tree_count(), 1)

    def test_remove_tree(self):
        self.forest.add_tree(self.tree)
        self.forest.remove_tree(self.tree)
        self.assertEqual(self.forest.get_tree_count(), 0)

if __name__ == '__main__':
    unittest.main()
