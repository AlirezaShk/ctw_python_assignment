from .base import BaseFactory
from lib.utils import load_test_fixture
from json import load as jsload
from lib.avantage_api import AlphaVantageAPI, DailyTimeSeriesRecord as OriginalModel


class DailyTimeSeriesRecords(BaseFactory):
    @classmethod
    def mock(_):
        return jsload(load_test_fixture("sample_avantage_dts_adj.json"))


class DailyTimeSeriesRecord(BaseFactory):
    @classmethod
    def mock(cls):
        record = {"1. open": cls.fake.pyfloat(), "4. close": cls.fake.pyfloat(), "6. volume": cls.fake.pyint()}
        return OriginalModel(
            record=record,
            date=cls.fake.date_between(),
            symbol=cls.fake.enum(AlphaVantageAPI.VALID_SYMBOLS)
        )
