from conf.settings import FIXTURES_DIR
import json
from pathlib import Path
from typing import Dict


def load_err_messages() -> Dict[str, str]:
    return json.load(open(Path(FIXTURES_DIR, "error_msg.json"), "r"))
