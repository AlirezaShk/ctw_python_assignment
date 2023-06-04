import mock
from mock import Mock
from financial.get_statistics import calc_mean, main as get_statistics
from faker.factory import Factory
from conf.settings import DEFAULT_DATE_FMT
from tests.factories.financial_data import FinancialData as FDFactory
from flask_sqlalchemy import BaseQuery


Faker = Factory.create
faker = Faker()
faker.seed(hash(__file__))


class TestGetStatisticsService:
    def sample_query(self, symbol: str = FDFactory.rand_symb().name):
        d1 = faker.date_between()
        d2 = faker.date_between(d1).strftime(DEFAULT_DATE_FMT)
        return {"start_date": d1.strftime(DEFAULT_DATE_FMT), "end_date": d2, "symbol": symbol}

    @mock.patch.object(BaseQuery, "count", return_value=0)
    def test_no_records(self, *args, **kwargs):
        assert get_statistics(**self.sample_query()) == {}

    @mock.patch.object(BaseQuery, "count", return_value=3)
    def test_with_records(self, *args, **kwargs):
        next_page = Mock()
        next_page.items = []
        paginated_results = Mock()
        paginated_results.items = [FDFactory.mock() for _ in range(3)]
        symbol = FDFactory.rand_symb().name
        for i in range(3):
            paginated_results.items[i].symbol = symbol
        paginated_results.next = (lambda: next_page)
        stats = calc_mean(paginated_results, columns=['symbol', 'open_price', 'close_price', 'volume'])
        with mock.patch.object(BaseQuery, "paginate", return_value=paginated_results):
            res = get_statistics(**self.sample_query(symbol))
            assert res["average_daily_open_price"] == stats.iloc[0]["open_price"]
            assert res["average_daily_close_price"] == stats.iloc[0]["close_price"]
            assert res["average_daily_volume"] == stats.iloc[0]["volume"]

    def test_calc(self):
        next_page = Mock()
        next_page.items = []
        paginated_results = Mock()
        paginated_results.items = [FDFactory.mock() for _ in range(3)]
        symbol = FDFactory.rand_symb().name
        for i in range(1, 4):
            paginated_results.items[i-1].symbol = symbol
            paginated_results.items[i-1].open_price = float(i)  # sum = 6, mean = 2.0
            paginated_results.items[i-1].close_price = float(i**2)  # sum = 14, mean = 4.667
            paginated_results.items[i-1].volume = i**3  # sum = 36, mean = 12.0
        paginated_results.next = (lambda: next_page)
        res = calc_mean(paginated_results, columns=['symbol', 'open_price', 'close_price', 'volume'])
        assert abs(res.iloc[0]["open_price"] - 2.0) <= 0.0001
        assert abs(res.iloc[0]["close_price"] - 4.6667) <= 0.0001
        assert abs(res.iloc[0]["volume"] - 12) <= 0.0001
