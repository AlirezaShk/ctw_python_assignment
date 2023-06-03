from .utils import load_err_messages

err_msg = load_err_messages()


class DatabaseEngineUndefinedError(BaseException):
    def __init__(self, engine_name: str):
        super().__init__(f"{err_msg['app']['database_engine_undefined']}: {engine_name}")


class ApiKeyNotFoundError(FileNotFoundError):
    def __init__(self):
        super().__init__({err_msg['app']['api_key_not_found']})


class SymbolUndefinedError(NotImplementedError):
    def __init__(self, symbol: str):
        super().__init__(f"{err_msg['app']['symbol_undefined']}: {symbol}")
