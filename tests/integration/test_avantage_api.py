import mock
import pytest
from lib.avantage_api import AlphaVantageAPI, DailyTimeSeriesRecord
from lib.exceptions import SymbolUndefinedError
from random import choice as rsample
from tests.factories.avantage_resp import DailyTimeSeriesRecords as DTSRsFactory
import requests

client = AlphaVantageAPI('sample', func="TIME_SERIES_DAILY_ADJUSTED")
sample_symbol = (lambda: rsample(list(AlphaVantageAPI.VALID_SYMBOLS.as_set())))


@mock.patch('requests.get', return_value=requests.models.Response())
@mock.patch('requests.models.Response.json',
            return_value=DTSRsFactory.mock())
def test_avantage_daily(*args, **kwargs):
    subject = (lambda: client._get_daily_data_json(sample_symbol().name))
    data = subject()
    assert isinstance(data, dict)
    time_series_data = data[client.FUNC_DATA_KEY[client.func]]
    k, v = ("2023-06-02", {
        "1. open": "130.38",
        "2. high": "133.12",
        "3. low": "130.15",
        "4. close": "132.42",
        "5. adjusted close": "132.42",
        "6. volume": "5375796",
        "7. dividend amount": "0.0000",
        "8. split coefficient": "1.0"
    })
    assert time_series_data[k] == v
    k, v = ("2023-06-02", {
        "1. open": "130.38",
        "2. high": "133.12",
        "3. low": "130.15",
        "4. close": "132.42",
        "5. adjusted close": "132.42",
        "6. volume": "5375796",
        "7. dividend amount": "0.0000",
        "8. split coefficient": "1.0"
    })
    assert time_series_data[k] == v


def test_standardize_symbol():
    subject = (lambda sym: client._standardize_symbol(sym))
    for symbol_code in AlphaVantageAPI.VALID_SYMBOLS.as_set(codes_only=True):
        assert symbol_code == subject(symbol_code)
    for symbol in AlphaVantageAPI.VALID_SYMBOLS.as_set():
        assert symbol.name == subject(symbol)
    with pytest.raises(SymbolUndefinedError):
        subject("X")


def test_get_parser():
    if client.func == "TIME_SERIES_DAILY_ADJUSTED":
        assert client._get_parser() == DailyTimeSeriesRecord


@mock.patch('lib.avantage_api.AlphaVantageAPI._get_daily_data_json',
            return_value=DTSRsFactory.mock())
def test_get_biweekly_data(*args, **kwargs):
    subject = (lambda sym: client.get_biweekly_data(sym))
    sym = sample_symbol()
    for s in [sym, sym.name]:
        res = subject(s)
        assert len(res) == 2
        for fd in res:
            assert isinstance(fd, dict)
            assert fd["updated_at"] is not None
            assert fd["date"] is not None
            assert fd["open_price"] is not None
            assert fd["close_price"] is not None
            assert fd["symbol"] == sym.name
            with pytest.raises(KeyError):
                assert fd["id"] is None
                assert fd["created_at"] is None
