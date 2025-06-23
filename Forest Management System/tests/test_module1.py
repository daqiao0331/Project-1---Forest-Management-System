import unittest
from project_name.module1 import Calculator

class TestCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)

    def test_substract(self):
        self.assertEqual(self.calc.substract(10, 5), 5)
        self.assertEqual(self.calc.substract(-1, -1), 0)

if __name__ == '__main__':
    unittest.main()
