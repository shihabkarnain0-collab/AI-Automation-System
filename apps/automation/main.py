import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_module(module_name):
    print("\n" + "=" * 60)
    print(f"Running: {module_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=PROJECT_ROOT
    )

    if result.returncode == 0:
        print("\n✓ Completed successfully.")
    else:
        print(f"\n✗ Failed with exit code: {result.returncode}")


def show_file(relative_path):
    file_path = PROJECT_ROOT / relative_path

    print("\n" + "=" * 60)
    print(f"OUTPUT: {relative_path}")
    print("=" * 60)

    if not file_path.exists():
        print("Output file not found.")
        return

    print(file_path.read_text(encoding="utf-8"))


def full_automation():
    print("\n")
    print("=" * 60)
    print("STARTING FULL AUTOMATION")
    print("=" * 60)

    run_module("apps.automation.discovery")
    run_module("apps.automation.research.research")
    run_module("apps.automation.analysis")
    run_module("apps.automation.affiliate")
    run_module("apps.automation.content")

    print("\n" + "=" * 60)
    print("FULL AUTOMATION COMPLETED")
    print("=" * 60)


def menu():
    while True:
        print("\n")
        print("=" * 60)
        print("        AI AUTOMATION SYSTEM")
        print("=" * 60)

        print("1.  Run Product Discovery")
        print("2.  Run Product Research")
        print("3.  Run Product Analysis")
        print("4.  Generate Affiliate Links")
        print("5.  Generate Marketing Content")
        print("6.  Run FULL Automation")
        print()
        print("7.  View Discovery Output")
        print("8.  View Research Output")
        print("9.  View Analysis Output")
        print("10. View Affiliate Output")
        print("11. View Content Output")
        print()
        print("0.  Exit")
        print("=" * 60)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            run_module("apps.automation.discovery")

        elif choice == "2":
            run_module("apps.automation.research.research")

        elif choice == "3":
            run_module("apps.automation.analysis")

        elif choice == "4":
            run_module("apps.automation.affiliate")

        elif choice == "5":
            run_module("apps.automation.content")

        elif choice == "6":
            full_automation()

        elif choice == "7":
            show_file("apps/automation/data/discovery/latest.json")

        elif choice == "8":
            show_file("apps/automation/data/research/latest.json")

        elif choice == "9":
            show_file("apps/automation/data/analysis/latest.json")

        elif choice == "10":
            show_file("apps/automation/data/affiliate/latest.json")

        elif choice == "11":
            show_file("apps/automation/data/content/latest.json")

        elif choice == "0":
            print("\nExiting AI Automation System...")
            break

        else:
            print("\nInvalid choice. Please select a number from 0-11.")


if __name__ == "__main__":
    menu()