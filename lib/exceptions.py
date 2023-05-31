from conf.settings import FIXTURES_DIR
import json
from pathlib import Path

err_msg = json.load(open(Path(FIXTURES_DIR, "error_msg.json"), "r"))
class DatabaseEngineUndefined(BaseException):
    def __init__(self, engine_name: str):
        super().__init__(f"{err_msg['app']['database_engine_undefined']}: {engine_name}")
