from typing import List
from abc import ABC, abstractmethod
from .exceptions import DatabaseEngineUndefinedError
from conf.settings import FIXTURES_DIR, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DB_PORT, DB_DIR, DEBUG
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from conf.settings import MAX_BULK_OPERATIONS
import contextlib


def get_schema_file():
    return open(Path(FIXTURES_DIR, "schema.sql"), "r")


class BaseDatabase(ABC):
    """General core interface for any database engine of this application.

    Methods:
        - initialize: Setup DB
        - prepare_transaction: Open a DB Connection/Session
        - submit_transaction: Commit changes to Database
        - prepare_transaction: End the DB Connection
    """
    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def prepare_transaction(self): pass

    @abstractmethod
    def submit_transaction(self): pass

    @abstractmethod
    def end_transaction(self): pass


class SQLAlchemyDatabase(BaseDatabase):
    """Parent class for all engines defined under SQLAlchemy module.

    SQLAlchemy is the only defined kind of Database router for this project at
    the moment.
    It comes with a constant `MAX_BULK_OPERATIONS` restricting the number of
    changes to be committed to the database per one transaction. This is to
    accommodate large queries, and increase robustness, and reduce load on
    DB Writers.
    """
    MAX_BULK_OPERATIONS = MAX_BULK_OPERATIONS
    session = None

    def initialize(self):
        self.core.init_app(self.app)
        self.core.create_all()

    def prepare_transaction(self):
        self.session = self.core.create_scoped_session()

    def end_transaction(self) -> None:
        self.session.close()
        self.session = None

    def submit_transaction(self) -> None:
        self.session.flush()
        self.session.commit()

    @contextlib.contextmanager
    def graceful_session_handler(self) -> None:
        """Sets up and tears down a DB Session, as a context manager.
        """
        auto_created = False
        if not self.session:
            auto_created = True
            self.prepare_transaction()

        yield

        if auto_created:
            self.end_transaction()

    def bulk_upsert(self, cls: type, objects: List[object]) -> None:
        with self.graceful_session_handler():
            for i, obj in enumerate(objects):
                self.session.merge(obj)
                if i > 0 and i % self.MAX_BULK_OPERATIONS == 0:
                    self.submit_transaction()
            self.submit_transaction()


class SQLite(SQLAlchemyDatabase):
    def __init__(self, app: object, path: str = DB_DIR):
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLite.conncetion_uri(
            path=path
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.core = SQLAlchemy(app)
        self.app = app

    @staticmethod
    def conncetion_uri(path):
        return f"sqlite:///{Path(path, 'sqlite.db')}"

    def bulk_upsert(self, cls: type, objects: List[object]):
        """Bulk upsert operation. This feature is not supported by SQLite.

        Using (Flask-SQLAlchemy==3.0.2), the model's UniqueConstraint does
        not properly trigger the right upsert operation on SQLite side. Hence
        in case this operation is performed in NO DEBUG mode, (e.g. in prod
        env) it will raise an error.

        Raises:
            NotImplementedError: (Read Above)
        """
        if not DEBUG:
            raise NotImplementedError("UniqueConstraint Does Not Work on SQLite")
        super().bulk_upsert(cls, objects)


class MySQL(SQLAlchemyDatabase):
    def __init__(self, app: object):
        app.config['SQLALCHEMY_DATABASE_URI'] = MySQL.conncetion_uri(
            username=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT, database_name=DB_NAME
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.core = SQLAlchemy(app)
        self.app = app

    @staticmethod
    def conncetion_uri(username: str, password: str, host: str, port: int | str, database_name: str) -> str:
        return f"mysql://{username}:{password}@{host}:{port}/{database_name}"


class DatabaseRouter:
    """A Factory class. Return the proper Database Class, based on the requested engine.

    Raises:
        DatabaseEngineUndefinedError: if engine_name is not defined.

    Returns:
        - MySQL
        - SQLite
    """
    @staticmethod
    def getDatabaseClient(engine: str) -> type:
        match engine:
            case "mysql":
                return MySQL
            case "sqlite":
                return SQLite
            case _:
                raise DatabaseEngineUndefinedError(engine_name=engine)
