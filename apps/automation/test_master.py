import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

import master
from master import AUTOMATION_DIR, PIPELINE


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

    @patch("master.subprocess.run")
    def test_nonzero_stage_exit_stops_pipeline(self, mock_run):
        mock_run.side_effect = [
            subprocess.CompletedProcess(args=[], returncode=0),
            subprocess.CompletedProcess(args=[], returncode=7),
        ]

        with contextlib.redirect_stdout(io.StringIO()):
            result = master.main()

        self.assertEqual(result, 1)
        self.assertEqual(mock_run.call_count, 2)

    @patch("master.subprocess.run")
    def test_successful_stages_run_in_existing_sequence(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
        )

        with contextlib.redirect_stdout(io.StringIO()):
            result = master.main()

        self.assertEqual(result, 0)
        self.assertEqual(
            mock_run.call_args_list,
            [
                call(
                    [sys.executable, str(script)],
                    cwd=AUTOMATION_DIR,
                )
                for _, script in PIPELINE
            ],
        )


if __name__ == "__main__":
    unittest.main()
