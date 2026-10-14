import unittest
from analysis import calculate_discount, score_product


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


class ScoreProductSubstringTests(unittest.TestCase):
    def test_php_does_not_match_hp_market_term(self):
        result = score_product({
            "title": "PHP development",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["market_score"]),
            (0, 0),
        )

    def test_chair_does_not_match_ai_social_term(self):
        result = score_product({
            "title": "Chair",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["social_marketing_score"]),
            (0, 0),
        )

    def test_model_m1500_does_not_match_m1_performance_term(self):
        result = score_product({
            "title": "Model M1500",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["performance_score"]),
            (0, 0),
        )

    def test_standalone_ai_matches_social_term(self):
        result = score_product({
            "title": "AI",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["social_marketing_score"]),
            (2, 2),
        )

    def test_standalone_hp_matches_market_term(self):
        result = score_product({
            "title": "HP",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["market_score"]),
            (2, 2),
        )

    def test_ai_hyphenated_term_matches_social_term(self):
        result = score_product({
            "title": "AI-powered",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (result["score"], result["metrics"]["social_marketing_score"]),
            (2, 2),
        )

    def test_macbook_m1_matches_performance_term(self):
        result = score_product({
            "title": "MacBook M1",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (
                result["score"],
                result["metrics"]["performance_score"],
                result["metrics"]["social_marketing_score"],
            ),
            (5, 3, 2),
        )


if __name__ == "__main__":
    unittest.main()
