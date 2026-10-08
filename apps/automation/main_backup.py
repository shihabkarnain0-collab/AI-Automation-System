from dotenv import load_dotenv
import os

from apps.automation.research.research import research_status
from apps.automation.content.content import content_status
from apps.automation.analytics.analytics import analytics_status
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "AI Automation System")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def main():
    print(f"=== {APP_NAME} ===")
    print(f"Environment: {ENVIRONMENT}")
    print(research_status())
    print(content_status())
    print(analytics_status())
    print("============================")


if __name__ == "__main__":
    main()
