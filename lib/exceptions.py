"""General exceptions used in the application.

DatabaseEngineUndefinedError: If DB_ENGINE is not defined in DatabaseRouter class.
ApiKeyNotFoundError: If `conf/api_key` is not found.
SymbolUndefinedError: If the given symbol, is not defined.
PageOutofBoundsError: If requested page in a paginated result, is larger than max page.
"""
from .utils import load_err_messages

err_msg = load_err_messages()


class DatabaseEngineUndefinedError(NotImplementedError):
    def __init__(self, engine_name: str):
        super().__init__(f"{err_msg['app']['database_engine_undefined']}: {engine_name}")


class ApiKeyNotFoundError(FileNotFoundError):
    def __init__(self):
        super().__init__({err_msg['api']['api_key_not_found']})


class SymbolUndefinedError(ValueError):
    def __init__(self, symbol: str):
        super().__init__(f"{err_msg['app']['symbol_undefined']}: {symbol}")
