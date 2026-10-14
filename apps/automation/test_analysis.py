import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import analysis
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


class CrossFieldPhraseTests(unittest.TestCase):
    def test_core_i7_does_not_match_across_title_and_description(self):
        result = score_product({
            "title": "Core",
            "description": "i7",
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
            (0, 0, 0),
        )

    def test_in_stock_does_not_match_across_title_and_description(self):
        result = score_product({
            "title": "In",
            "description": "stock",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (
                result["score"],
                result["metrics"]["purchase_intent_score"],
            ),
            (0, 0),
        )

    def test_core_i7_matches_when_present_within_one_field(self):
        result = score_product({
            "title": "Core i7",
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

    def test_in_stock_matches_when_present_within_one_field(self):
        result = score_product({
            "title": "In stock",
            "description": "",
            "brand": "",
            "category": "",
            "specifications": {},
        })

        self.assertEqual(
            (
                result["score"],
                result["metrics"]["purchase_intent_score"],
            ),
            (2, 2),
        )


class ResearchStatusFilteringTests(unittest.TestCase):
    def analyze_products(self, products):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            research_file = temp_path / "research.json"
            output_dir = temp_path / "analysis"

            research_file.write_text(
                json.dumps({"products": products}),
                encoding="utf-8",
            )

            with (
                patch.object(analysis, "RESEARCH_FILE", research_file),
                patch.object(analysis, "OUTPUT_DIR", output_dir),
                patch.object(
                    analysis,
                    "OUTPUT_FILE",
                    output_dir / "latest.json",
                ),
            ):
                return analysis.run_analysis()

    def test_failed_record_with_data_is_excluded(self):
        result = self.analyze_products([
            {
                "research_status": "failed",
                "product_name": "Failed Laptop",
                "product_data": {"title": "16GB Laptop"},
            },
        ])

        self.assertEqual(result["valid_products"], 0)
        self.assertEqual(result["products"], [])
        self.assertIsNone(result["best_product"])

    def test_completed_record_with_data_remains_eligible(self):
        result = self.analyze_products([
            {
                "research_status": "completed",
                "product_name": "Valid Laptop",
                "product_data": {
                    "title": "16GB Laptop",
                    "specifications": {},
                },
            },
        ])

        self.assertEqual(result["valid_products"], 1)
        self.assertEqual(
            result["products"][0]["product_name"],
            "16GB Laptop",
        )
        self.assertEqual(
            result["products"][0]["research_status"],
            "completed",
        )

    def test_completed_record_with_all_empty_extracted_data_is_excluded(self):
        result = self.analyze_products([
            {
                "research_status": "completed",
                "product_data": {
                    "title": None,
                    "description": None,
                    "price": None,
                    "old_price": None,
                    "discount": None,
                    "availability": None,
                    "brand": None,
                    "category": None,
                    "image": None,
                    "specifications": {},
                },
            },
        ])

        self.assertEqual(result["valid_products"], 0)
        self.assertEqual(result["products"], [])

    def test_completed_record_with_non_dictionary_data_is_excluded(self):
        result = self.analyze_products([
            {
                "research_status": "completed",
                "product_data": ["16GB Laptop"],
            },
        ])

        self.assertEqual(result["valid_products"], 0)
        self.assertEqual(result["products"], [])

    def test_missing_research_status_is_excluded(self):
        result = self.analyze_products([
            {
                "product_name": "Untracked Laptop",
                "product_data": {"title": "16GB Laptop"},
            },
        ])

        self.assertEqual(result["valid_products"], 0)
        self.assertEqual(result["products"], [])

    def test_missing_or_empty_product_data_is_excluded(self):
        for product in (
            {"research_status": "completed"},
            {
                "research_status": "completed",
                "product_data": None,
            },
            {
                "research_status": "completed",
                "product_data": {},
            },
        ):
            with self.subTest(product=product):
                result = self.analyze_products([product])

                self.assertEqual(result["valid_products"], 0)
                self.assertEqual(result["products"], [])


class FeatureGroupScoringTests(unittest.TestCase):
    def score_title(self, title, specifications=None):
        return score_product({
            "title": title,
            "description": "",
            "brand": "",
            "category": "",
            "specifications": specifications or {},
        })

    def test_core_ultra_7_scores_one_social_feature_group(self):
        result = self.score_title("Core Ultra 7")

        self.assertEqual(
            (
                result["metrics"]["performance_score"],
                result["metrics"]["social_marketing_score"],
                result["score"],
            ),
            (3, 2, 5),
        )

    def test_16gb_scores_in_approved_categories(self):
        result = self.score_title("16GB")

        self.assertEqual(
            (
                result["metrics"]["performance_score"],
                result["metrics"]["market_score"],
                result["metrics"]["social_marketing_score"],
                result["score"],
            ),
            (3, 2, 2, 7),
        )

    def test_ssd_scores_in_market_and_purchase_intent(self):
        result = self.score_title("SSD")

        self.assertEqual(
            (
                result["metrics"]["market_score"],
                result["metrics"]["purchase_intent_score"],
                result["score"],
            ),
            (2, 2, 4),
        )

    def test_gaming_scores_in_social_marketing(self):
        result = self.score_title("Gaming")

        self.assertEqual(
            (result["metrics"]["social_marketing_score"], result["score"]),
            (2, 2),
        )

    def test_in_stock_scores_in_purchase_intent(self):
        result = self.score_title("In stock")

        self.assertEqual(
            (result["metrics"]["purchase_intent_score"], result["score"]),
            (2, 2),
        )

    def test_feature_in_title_and_specifications_scores_once_per_category(self):
        result = self.score_title(
            "16GB",
            specifications={"Memory": "16GB"},
        )

        self.assertEqual(
            (
                result["metrics"]["performance_score"],
                result["metrics"]["market_score"],
                result["metrics"]["social_marketing_score"],
                result["score"],
            ),
            (3, 2, 2, 7),
        )

    def test_category_scores_respect_caps(self):
        result = self.score_title(
            "Core i5 Core i7 Core Ultra Ryzen 5 Ryzen 7 Ryzen AI "
            "M1 M2 M3 M4 M5 16GB 32GB 512GB 1TB RTX "
            "Laptop FHD SSD 8GB Intel AMD Ryzen Apple Lenovo HP "
            "Dell Acer Asus MSI "
            "In stock RAM Processor Price Order online "
            "Gaming MacBook AI OLED Touch Ultra"
        )

        self.assertEqual(
            result["metrics"],
            {
                "performance_score": 20,
                "market_score": 15,
                "purchase_intent_score": 10,
                "social_marketing_score": 10,
            },
        )

    def test_discount_tier_boundaries_and_final_score(self):
        cases = [
            (10000, 10000, 0, 17),
            (9501, 10000, 4.99, 22),
            (9500, 10000, 5, 25),
            (9001, 10000, 9.99, 25),
            (9000, 10000, 10, 29),
            (8001, 10000, 19.99, 29),
            (8000, 10000, 20, 32),
        ]

        for price, old_price, expected_discount, expected_score in cases:
            with self.subTest(discount=expected_discount):
                result = score_product({
                    "title": "",
                    "description": "",
                    "brand": "",
                    "category": "",
                    "price": price,
                    "old_price": old_price,
                    "specifications": {},
                })

                self.assertEqual(result["discount_percent"], expected_discount)
                self.assertEqual(result["score"], expected_score)

    def test_final_score_remains_capped_at_100(self):
        result = score_product({
            "title": (
                "Core i5 Core i7 Core Ultra Ryzen 5 Ryzen 7 Ryzen AI "
                "M1 M2 M3 M4 M5 16GB 32GB 512GB 1TB RTX "
                "Laptop FHD SSD 8GB Intel AMD Ryzen Apple Lenovo HP "
                "Dell Acer Asus MSI "
                "In stock RAM Processor Price Order online "
                "Gaming MacBook AI OLED Touch Ultra"
            ),
            "description": "",
            "brand": "",
            "category": "",
            "price": 50000,
            "old_price": 62500,
            "specifications": {},
        })

        self.assertEqual(result["score"], 100)


class PriceAndAffiliateBoundaryTests(unittest.TestCase):
    def score_price(self, price):
        return score_product({
            "title": "",
            "description": "",
            "brand": "",
            "category": "",
            "price": price,
            "specifications": {},
        })

    def test_price_scoring_boundaries(self):
        cases = [
            (19999, 17, "Very low price"),
            (20000, 22, "Highly affordable price"),
            (20001, 22, "Highly affordable price"),
            (29999, 25, "Highly affordable price"),
            (30000, 28, "Strong mainstream price range"),
            (30001, 28, "Strong mainstream price range"),
            (79999, 30, "Strong mainstream price range"),
            (80000, 30, "Strong mainstream price range"),
            (80001, 25, "Premium but still marketable price"),
            (119999, 25, "Premium but still marketable price"),
            (120000, 25, "Premium but still marketable price"),
            (120001, 17, "High-ticket product"),
            (159999, 17, "High-ticket product"),
            (160000, 17, "High-ticket product"),
            (160001, 13, "Very high price"),
        ]

        for price, expected_score, expected_price_reason in cases:
            with self.subTest(price=price):
                result = self.score_price(price)

                self.assertEqual(result["score"], expected_score)
                self.assertIn(expected_price_reason, result["reasons"])

    def test_affiliate_scoring_boundaries(self):
        cases = [
            (24999, 22, None),
            (25000, 25, "Good entry-level affiliate value"),
            (25001, 25, "Good entry-level affiliate value"),
            (39999, 28, "Good entry-level affiliate value"),
            (40000, 30, "Good affiliate-value range"),
            (40001, 30, "Good affiliate-value range"),
            (119999, 25, "Good affiliate-value range"),
            (120000, 25, "Good affiliate-value range"),
            (120001, 17, "High-ticket affiliate opportunity"),
        ]

        for price, expected_score, expected_affiliate_reason in cases:
            with self.subTest(price=price):
                result = self.score_price(price)

                self.assertEqual(result["score"], expected_score)
                if expected_affiliate_reason is None:
                    self.assertNotIn(
                        "Good entry-level affiliate value",
                        result["reasons"],
                    )
                    self.assertNotIn(
                        "Good affiliate-value range",
                        result["reasons"],
                    )
                    self.assertNotIn(
                        "High-ticket affiliate opportunity",
                        result["reasons"],
                    )
                else:
                    self.assertIn(
                        expected_affiliate_reason,
                        result["reasons"],
                    )


if __name__ == "__main__":
    unittest.main()
