import os
from dotenv import load_dotenv

# Load .env once
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "60"))

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")

APP_NAME = os.getenv("APP_NAME", "FYP Auth API")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
