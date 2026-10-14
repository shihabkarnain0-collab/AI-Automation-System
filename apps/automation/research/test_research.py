import unittest
from unittest.mock import patch

from product_data import is_usable_product_data
import research


class ProductDataValidityTests(unittest.TestCase):
    def test_normal_extracted_product_data_is_usable(self):
        product_data = {
            "title": "Laptop A",
            "description": None,
            "price": "৳50,000",
            "old_price": None,
            "discount": None,
            "availability": "In stock",
            "brand": None,
            "category": None,
            "image": None,
            "specifications": {"Memory": "16GB"},
        }

        self.assertTrue(is_usable_product_data(product_data))

    def test_nonempty_extracted_specifications_are_usable_without_title(self):
        self.assertTrue(
            is_usable_product_data({
                "title": None,
                "specifications": {"Memory": "16GB"},
            })
        )

    def test_all_empty_extracted_values_are_not_usable(self):
        product_data = {
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
        }

        self.assertFalse(is_usable_product_data(product_data))

    def test_non_dictionary_product_data_is_not_usable(self):
        for product_data in ("Laptop A", ["Laptop A"], None):
            with self.subTest(product_data=product_data):
                self.assertFalse(is_usable_product_data(product_data))

    def test_non_dictionary_specifications_are_not_usable(self):
        self.assertFalse(
            is_usable_product_data({
                "title": "Laptop A",
                "specifications": [],
            })
        )


class BatchProductResearchTests(unittest.TestCase):
    def run_batch(self, urls, results):
        with (
            patch.object(
                research,
                "load_discovery",
                return_value={"product_urls": urls},
            ),
            patch.object(
                research,
                "product_research",
                side_effect=results,
            ) as mock_product_research,
        ):
            result = research.batch_product_research()

        return result, mock_product_research

    def test_all_successful_products_report_completed(self):
        products = [
            {
                "research_status": "completed",
                "product_data": {"title": "Laptop A"},
            },
            {
                "research_status": "completed",
                "product_data": {"title": "Laptop B"},
            },
        ]

        result, _ = self.run_batch(
            ["url-a", "url-b"],
            products,
        )

        self.assertEqual(result["research_status"], "completed")
        self.assertEqual(result["successful_product_count"], 2)
        self.assertEqual(result["failed_product_count"], 0)
        self.assertEqual(result["products"], products)

    def test_mixed_results_report_partial_and_preserve_product_details(self):
        products = [
            {
                "research_status": "completed",
                "product_data": {"title": "Laptop A"},
            },
            {
                "research_status": "failed",
                "product_data": None,
                "error": "Request failed",
            },
        ]

        result, _ = self.run_batch(
            ["url-a", "url-b"],
            products,
        )

        self.assertEqual(result["research_status"], "partial")
        self.assertEqual(result["successful_product_count"], 1)
        self.assertEqual(result["failed_product_count"], 1)
        self.assertEqual(result["products"], products)

    def test_all_failures_report_failed_with_counts(self):
        products = [
            {
                "research_status": "failed",
                "product_data": None,
                "error": "Request failed",
            },
            {
                "research_status": "failed",
                "product_data": None,
                "error": "Extraction failed",
            },
        ]

        result, _ = self.run_batch(
            ["url-a", "url-b"],
            products,
        )

        self.assertEqual(result["research_status"], "failed")
        self.assertEqual(result["successful_product_count"], 0)
        self.assertEqual(result["failed_product_count"], 2)
        self.assertEqual(result["products"], products)

    def test_no_products_reports_failed_with_zero_counts(self):
        result, mock_product_research = self.run_batch([], [])

        self.assertEqual(result["research_status"], "failed")
        self.assertEqual(result["successful_product_count"], 0)
        self.assertEqual(result["failed_product_count"], 0)
        self.assertEqual(result["products"], [])
        mock_product_research.assert_not_called()

    def test_completed_result_without_product_data_is_not_a_success(self):
        products = [
            {
                "research_status": "completed",
                "product_data": {},
            },
        ]

        result, _ = self.run_batch(["url-a"], products)

        self.assertEqual(result["research_status"], "failed")
        self.assertEqual(result["successful_product_count"], 0)
        self.assertEqual(result["failed_product_count"], 1)

    def test_empty_extracted_values_are_not_a_success(self):
        products = [
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
        ]

        result, _ = self.run_batch(["url-a"], products)

        self.assertEqual(result["research_status"], "failed")
        self.assertEqual(result["successful_product_count"], 0)
        self.assertEqual(result["failed_product_count"], 1)

    def test_non_dictionary_product_data_is_not_a_success(self):
        products = [
            {
                "research_status": "completed",
                "product_data": ["Laptop A"],
            },
        ]

        result, _ = self.run_batch(["url-a"], products)

        self.assertEqual(result["research_status"], "failed")
        self.assertEqual(result["successful_product_count"], 0)
        self.assertEqual(result["failed_product_count"], 1)


if __name__ == "__main__":
    unittest.main()
