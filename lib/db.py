from typing import List
from abc import ABC, abstractmethod
from .exceptions import DatabaseEngineUndefined
from conf.settings import FIXTURES_DIR, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DB_PORT, DB_DIR
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy, model


def get_schema_file():
    return open(Path(FIXTURES_DIR, "schema.sql"), "r")


class BaseDatabase(ABC):
    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def execute(self, querys: List[str]): pass


class SQLAlchemyDatabase(BaseDatabase):
    def initialize(self):
        self.conn.create_all()

    def execute(self, querys: List[str]) -> None:
        cursor = self.conn.connection.cursor()
        for query in querys:
            cursor.execute(query)
        self.conn.connection.commit()
        cursor.close()

    def enqueue(self, obj: model.DefaultMeta) -> None:
        self.conn.session.add(obj)

    def commit(self):
        self.conn.session.commit()
        self.conn.session.flush()



class SQLite(SQLAlchemyDatabase):
    def __init__(self, app):
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLite.conncetion_uri(
            path=DB_DIR
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.conn = SQLAlchemy(app)

    @staticmethod
    def conncetion_uri(path):
        return f"sqlite:///{Path(path, 'sqlite.db')}"


class MySQL(SQLAlchemyDatabase):
    def __init__(self, app):
        app.config['SQLALCHEMY_DATABASE_URI'] = MySQL.conncetion_uri(
            username=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT, database_name=DB_NAME
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.conn = SQLAlchemy(app)

    @staticmethod
    def conncetion_uri(username, password, host, port, database_name):
        return f"mysql://{username}:{password}@{host}:{port}/{database_name}"


class DatabaseRouter:
    @staticmethod
    def getDatabaseClient(engine: str) -> type:
        match engine:
            case "mysql":
                return MySQL
            case "sqlite":
                return SQLite
            case _:
                raise DatabaseEngineUndefined(engine_name=engine)
