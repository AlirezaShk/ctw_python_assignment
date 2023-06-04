import pytest
import mock
from mock import call as mcall
from app import db
from lib.avantage_api import AlphaVantageAPI
from lib.utils import load_test_fixture
from lib.exceptions import ApiKeyNotFoundError
from get_raw_data import execute, get_api_key
from tests.factories.avantage_resp import DailyTimeSeriesRecord


@mock.patch('builtins.open', side_effect=FileNotFoundError())
def test_get_api_key_error(*args, **kwargs):
    subject = (lambda: get_api_key())
    with pytest.raises(ApiKeyNotFoundError):
        print(subject())


@mock.patch('builtins.open', return_value=load_test_fixture("api_key"))
def test_get_api_key_ok(*args, **kwargs):
    subject = (lambda: get_api_key())
    assert subject() == "HelloWorld!"


def test_execute_calling_api_biweekly(*args, **kwargs):
    subject = (lambda: execute())
    expected_api_calls = list(map(lambda x: mcall(x), AlphaVantageAPI.VALID_SYMBOLS.as_set()))
    expected_db_submit_calls = list(map(lambda x: mcall(), AlphaVantageAPI.VALID_SYMBOLS.as_set()))

    with mock.patch.object(db.__class__, "submit_transaction", return_value=[]) as db_transaction:
        with mock.patch.object(AlphaVantageAPI, "get_biweekly_data", return_value=[]) as api_call:
            subject()
            api_call.assert_has_calls(expected_api_calls, any_order=True)
            db_transaction.assert_has_calls(expected_db_submit_calls, any_order=True)


def test_execute_db_transactions():
    subject = (lambda: execute())
    records = [DailyTimeSeriesRecord.mock().to_model() for _ in range(3)]
    # Once for each symbol
    expected_calls = [mcall() for _ in range(len(AlphaVantageAPI.VALID_SYMBOLS))]

    with mock.patch.object(AlphaVantageAPI, "get_biweekly_data", return_value=records):
        with mock.patch('builtins.open', return_value=load_test_fixture("api_key")):
            with mock.patch.object(db.__class__, "submit_transaction", return_value=[]) as db_submit_transaction:
                subject()
                db_submit_transaction.assert_has_calls(expected_calls)
