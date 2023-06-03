from model import FinancialData
from tests.factories.avantage_resp import DailyTimeSeriesRecords as DTSRsFactory
from lib.avantage_api import AlphaVantageAPI, DailyTimeSeriesRecord
from conf.settings import DEFAULT_DATE_FMT
from random import choice as rsample
from datetime import datetime


def test_dtsr_to_x():
    resp = DTSRsFactory.mock()
    client = AlphaVantageAPI('sample', func="TIME_SERIES_DAILY_ADJUSTED")
    records_dict = resp[client.FUNC_DATA_KEY[client.func]]
    sample_date_key = rsample(list(records_dict.keys()))
    symbol = rsample(list(AlphaVantageAPI.VALID_SYMBOLS.as_set(codes_only=True)))
    transformed = DailyTimeSeriesRecord(
        record=records_dict[sample_date_key],
        date=datetime.strptime(sample_date_key, DEFAULT_DATE_FMT),
        symbol=symbol
    )

    actual_dict = transformed.to_dict()
    del actual_dict["updated_at"]
    expected_dict = {"symbol": symbol, "date": datetime.strptime(sample_date_key, DEFAULT_DATE_FMT), "open_price": records_dict[sample_date_key]["1. open"], "close_price": records_dict[sample_date_key]["4. close"], "volume": records_dict[sample_date_key]["6. volume"]}
    actual_obj = transformed.to_model()
    expected_obj = FinancialData(**expected_dict)

    # To Model
    assert actual_obj.updated_at is not None
    assert actual_obj == expected_obj
    # To Dict
    assert actual_dict == expected_dict
