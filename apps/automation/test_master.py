import unittest
from pathlib import Path

from master import PIPELINE


class MasterPipelineTests(unittest.TestCase):
    def test_analytics_stage_targets_analytics_implementation(self):
        analytics_script = next(
            script
            for label, script in PIPELINE
            if label.endswith("Analytics")
        )

        expected_script = (
            Path(__file__).resolve().parent
            / "analytics"
            / "analytics.py"
        )

        self.assertEqual(analytics_script, expected_script)
        self.assertTrue(analytics_script.is_file())


if __name__ == "__main__":
    unittest.main()
