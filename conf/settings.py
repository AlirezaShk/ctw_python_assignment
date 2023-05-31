import os
import dotenv

dotenv.load_dotenv()

# - Environment:
APP_PORT = os.getenv("SERVER_PORT")
APP_ENV = os.getenv("APP_ENV")
DEBUG = os.getenv("DEBUG") == "True"
LOGS_DIR = os.getenv("LOGS_PATH")
FIXTURES_DIR = os.getenv("FIXTURES_PATH")

# - Database
DB_HOST = os.getenv("DB_HOST")
DB_PORT = 3306
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
