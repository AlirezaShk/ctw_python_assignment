"""Integartion tests -> View tests. Testing the endpoints of the application.
"""
from contextlib import contextmanager
from flask import Flask
from flask_restx import Api
from routes import api as ns


@contextmanager
def test_client(*args, **kwargs):
    app = Flask("test")
    app.testing = True
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    api = Api(app, doc="/api", prefix="/api")
    api.add_namespace(ns)
    with app.test_client() as client:
        yield client
    app.testing = False
    app.config.update({
        "TESTING": False,
    })
