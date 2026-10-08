from dotenv import load_dotenv
import os

load_dotenv()

print("APP_NAME:", os.getenv("APP_NAME"))
print("ENVIRONMENT:", os.getenv("ENVIRONMENT"))
