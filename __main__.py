"""Main application server starter.

    This file is used to:
        1. Initialize Cache and DB
        2. Register API Namespaces (refer to routes.py)
        3. Initialize the application server
"""
from app import app as application, db, api, cache
from conf.settings import DEBUG, APP_PORT
from routes import api as ns

api.add_namespace(ns)

with application.app_context():
    cache.init_app(application)
    db.initialize()

application.run(debug=DEBUG, use_reloader=True, host="0.0.0.0", port=APP_PORT)
