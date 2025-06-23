import unittest
from project_name.tree import Tree
from project_name.utils import find_trees_by_health, count_trees_by_species

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.trees = [
            Tree('Pine', 10, 'Healthy'),
            Tree('Oak', 5, 'Sick'),
            Tree('Pine', 7, 'Healthy'),
        ]

    def test_find_trees_by_health(self):
        healthy = find_trees_by_health(self.trees, 'Healthy')
        self.assertEqual(len(healthy), 2)

    def test_count_trees_by_species(self):
        species_count = count_trees_by_species(self.trees)
        self.assertEqual(species_count['Pine'], 2)
        self.assertEqual(species_count['Oak'], 1)

if __name__ == '__main__':
    unittest.main()
