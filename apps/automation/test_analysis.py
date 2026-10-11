import unittest
from analysis import calculate_discount


class CalculateDiscountTests(unittest.TestCase):
    def test_normal_discount(self):
        self.assertAlmostEqual(calculate_discount(40000, 50000), 20.0, places=2)

    def test_rounds_to_two_decimals(self):
        self.assertAlmostEqual(calculate_discount(33.333, 100), 66.67, places=2)

    def test_equal_prices_give_zero(self):
        self.assertEqual(calculate_discount(50000, 50000), 0)

    def test_price_higher_than_old_price_gives_zero(self):
        self.assertEqual(calculate_discount(55000, 50000), 0)

    def test_missing_prices_give_zero(self):
        self.assertEqual(calculate_discount(None, 50000), 0)
        self.assertEqual(calculate_discount(50000, None), 0)
        self.assertEqual(calculate_discount(None, None), 0)

    def test_zero_prices_give_zero(self):
        self.assertEqual(calculate_discount(0, 50000), 0)
        self.assertEqual(calculate_discount(50000, 0), 0)


if __name__ == "__main__":
    unittest.main()
