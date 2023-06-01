from flask import Flask
from flask_restful import Api
from flask_mysqldb import MySQL
from __init__ import __proj_name__
import logging
import dotenv
import os
from pathlib import Path
from conf.settings import APP_ENV, LOGS_DIR
from lib.db import DatabaseRouter
from flask_cors import CORS


dotenv.load_dotenv()

# Flask Initialization
app = Flask(f"{__proj_name__}")
api = Api(app)
CORS(app, origins=os.getenv("ALLOWED_HOSTS", "*").split(","))

# Application Configuration
# - Logger:
logging.basicConfig(
    filename=Path(LOGS_DIR, APP_ENV + '.log'),
    encoding='utf-8',
    format="(%(asctime)s)[%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

# Database Connection
db = DatabaseRouter.getDatabaseClient(engine=os.getenv("DB_ENGINE"))(app)
