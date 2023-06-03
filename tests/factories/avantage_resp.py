from .base import BaseFactory
from lib.utils import load_test_fixture


class DailyTimeSeriesRecords(BaseFactory):
    @classmethod
    def mock(_):
        return load_test_fixture("sample_avantage_dts_adj.json")
