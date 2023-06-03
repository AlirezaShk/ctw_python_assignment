from conf.settings import FIXTURES_DIR, TEST_FIXTURES_DIR
import json
from pathlib import Path
from typing import Dict


def load_err_messages() -> Dict[str, str]:
    return json.load(open(Path(FIXTURES_DIR, "error_msg.json"), "r"))


def load_help_messages() -> Dict[str, str]:
    return json.load(open(Path(FIXTURES_DIR, "help.json"), "r"))


def load_test_fixture(name: str) -> Dict[str, str]:
    return json.load(open(Path(TEST_FIXTURES_DIR, f"{name}"), "r"))
