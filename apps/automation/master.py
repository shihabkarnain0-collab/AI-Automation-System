import subprocess
import sys
from pathlib import Path


AUTOMATION_DIR = Path(__file__).resolve().parent

PIPELINE = [
    ("1/6 Discovery", AUTOMATION_DIR / "discovery.py"),
    ("2/6 Research", AUTOMATION_DIR / "research" / "research.py"),
    ("3/6 Analysis", AUTOMATION_DIR / "analysis.py"),
    ("4/6 Affiliate", AUTOMATION_DIR / "affiliate.py"),
    ("5/6 Content", AUTOMATION_DIR / "content.py"),
    ("6/6 Analytics", AUTOMATION_DIR / "analytics.py"),
]


def run_step(label, script):
    print("\n" + "=" * 60)
    print(label)
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=AUTOMATION_DIR
    )

    if result.returncode != 0:
        print(
            f"\nERROR: {script.name} failed "
            f"with exit code {result.returncode}."
        )
        return False

    print(f"\n✓ {script.name} completed successfully.")
    return True


def main():
    print("=== AI Automation System | MASTER RUNNER ===")

    for label, script in PIPELINE:

        if not script.exists():
            print(f"ERROR: Missing script: {script}")
            return 1

        if not run_step(label, script):
            print("\nPIPELINE STOPPED.")
            return 1

    print("\n" + "=" * 60)
    print("FULL AUTOMATION PIPELINE COMPLETED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
