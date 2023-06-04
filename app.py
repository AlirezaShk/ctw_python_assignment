from flask import Flask
from flask_restx import Api
from __init__ import __proj_name__, __version__
import logging
import dotenv
import os
from pathlib import Path
from conf.settings import APP_ENV, LOGS_DIR
from lib.db import DatabaseRouter
from flask_cors import CORS
from flask_caching import Cache


env_path = ".env.prod" if APP_ENV == 'prod' else None
dotenv.load_dotenv(env_path)

# TODO: Migrate from static application creation to Application Creator Factory design.
# This will supply the application with a flexible configurable feature.

# Flask Initialization
app = Flask(f"{__proj_name__}")
app.config['OPENAPI_VERSION'] = '3.0.2'
if APP_ENV == 'prod':
    CORS(app, origins=os.getenv("ALLOWED_HOSTS", "*").split(","))
api = Api(
    app,
    title=f"{__proj_name__} REST API",
    version=__version__,
    prefix="/api",
    doc="/api"
)

# Application Configuration
# - Logger:
logging.basicConfig(
    filename=Path(LOGS_DIR, APP_ENV + '.log'),
    encoding='utf-8',
    format="(%(asctime)s)[%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

# - Database Connection
db = DatabaseRouter.getDatabaseClient(engine=os.getenv("DB_ENGINE"))(app)

# - Cache
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)
