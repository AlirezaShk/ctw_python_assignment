from typing import List, Dict
from abc import ABC, abstractmethod
from .exceptions import DatabaseEngineUndefinedError
from conf.settings import FIXTURES_DIR, DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DB_PORT, DB_DIR
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy, model
from sqlalchemy.sql import text
from conf.settings import MAX_BULK_OPERATIONS


def get_schema_file():
    return open(Path(FIXTURES_DIR, "schema.sql"), "r")


class BaseDatabase(ABC):
    @abstractmethod
    def initialize(self): pass

    @abstractmethod
    def execute(self, querys: List[str]): pass


class SQLAlchemyDatabase(BaseDatabase):
    MAX_BULK_OPERATIONS = MAX_BULK_OPERATIONS

    def initialize(self):
        self.core.init_app(self.core.app)
        self.core.create_all()

    def execute(self, querys: List[str]) -> None:
        for query in querys:
            self.core.session.execute(text(query))
        self.commit()

    def enqueue(self, obj: model.DefaultMeta, upsert=False) -> None:
        if upsert:
            self.core.session.merge(obj)
        else:
            self.core.session.add(obj)

    def commit(self):
        self.core.session.commit()
        self.core.session.flush()


class SQLite(SQLAlchemyDatabase):
    def __init__(self, app: object, path: str = DB_DIR):
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLite.conncetion_uri(
            path=path
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.core = SQLAlchemy(app)

    @staticmethod
    def conncetion_uri(path):
        return f"sqlite:///{Path(path, 'sqlite.db')}"

    def bulk_upsert(self, cls: type, attrs: List[Dict]):
        table_statement, cols = cls.as_sql_table(only_required=True)
        # selecting table and operation
        definition = f"INSERT INTO {table_statement} VALUES "
        # duplication handling
        unique_cols = list(map(lambda x: x.name, cls.__table_args__[0].columns))
        duplication = f" ON CONFLICT({', '.join(unique_cols)}) DO UPDATE SET {', '.join((f'{col}=EXCLUDED.{col}' for col in cols))}"
        # values
        values = ""
        for i, attr in enumerate(attrs):
            values += "('" + "', '".join((str(attr[col]) for col in cols)) + "'), "
            if i % self.MAX_BULK_OPERATIONS == 0:
                self.execute([definition + values[:-2] + duplication])
                values = ""
        if len(values) > 6:
            self.execute([definition + values[:-2] + duplication])


class MySQL(SQLAlchemyDatabase):
    def __init__(self, app: object):
        app.config['SQLALCHEMY_DATABASE_URI'] = MySQL.conncetion_uri(
            username=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT, database_name=DB_NAME
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.core = SQLAlchemy(app)

    @staticmethod
    def conncetion_uri(username: str, password: str, host: str, port: int | str, database_name: str) -> str:
        return f"mysql://{username}:{password}@{host}:{port}/{database_name}"

    def bulk_upsert(self, cls: type, attrs: List[Dict]) -> None:
        table_statement, cols = cls.as_sql_table()
        # selecting table and operation
        definition = f"INSERT INTO {table_statement} VALUES "
        # duplication handling
        duplication = f" ON DUPLICATE KEY UPDATE {', '.join((f'{col}=VALUES({col})' for col in cols))}"
        # values
        values = ""
        for i, attr in enumerate(attrs):
            values += "('" + "', '".join((str(attr[col]) for col in cols)) + "'), "
            if i % self.MAX_BULK_OPERATIONS == 0:
                self.execute([definition + values[:-2] + duplication])
                values = ""
        if len(values) > 6:
            self.execute([definition + values[:-2] + duplication])


class DatabaseRouter:
    @staticmethod
    def getDatabaseClient(engine: str) -> type:
        match engine:
            case "mysql":
                return MySQL
            case "sqlite":
                return SQLite
            case _:
                raise DatabaseEngineUndefinedError(engine_name=engine)
