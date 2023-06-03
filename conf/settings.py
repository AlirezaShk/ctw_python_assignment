import os
import dotenv

dotenv.load_dotenv()

# - Environment:
APP_PORT = os.getenv("SERVER_PORT", "5000")
APP_ENV = os.getenv("APP_ENV", "dev")
DEBUG = os.getenv("DEBUG", "True") == "True"
LOGS_DIR = os.getenv("LOGS_PATH", "data/log")
FIXTURES_DIR = os.getenv("FIXTURES_PATH", "data/fixtures")
TEST_FIXTURES_DIR = os.getenv("TEST_FIXTURES_PATH", "tests/fixtures")
DB_DIR = os.getenv("DB_PATH", "data/streaming")
TEMP_DIR = os.getenv("TEMP_PATH", "temp")

# - Database Configuration:
DB_HOST = os.getenv("DB_HOST")
DB_PORT = 3306
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# - App Configuration:
MAX_BULK_OPERATIONS = 50
DEFAULT_DATE_FMT = "%Y-%m-%d"
