import mock
from tests.factories.financial_data import FinancialData as FDFactory
from faker.factory import Factory
from conf.settings import DEFAULT_DATE_FMT
from typing import Dict, Optional
from . import test_client
from json import loads as jsloads


Faker = Factory.create
faker = Faker()
faker.seed(hash(__file__))


class TestStatisticsView:
    ENDPOINT = "/api/statistics"

    def send_request(self, query_params: Optional[Dict] = {}, path: Optional[str] = ENDPOINT):
        with test_client() as client:
            return client.get(path, query_string=query_params)

    def sample_query(self):
        d1 = faker.date_between()
        d2 = faker.date_between(d1).strftime(DEFAULT_DATE_FMT)
        return {"start_date": d1.strftime(DEFAULT_DATE_FMT), "end_date": d2, "symbol": FDFactory.rand_symb().name}

    def sample_statitstics(self, symbol: str):
        return {
            'symbol': symbol,
            'average_daily_open_price': faker.pyfloat(),
            'average_daily_close_price': faker.pyfloat(),
            'average_daily_volume': faker.pyfloat()
        }

    # 400 Errors
    def test_invalid_gets(self):
        d1 = faker.date_between()
        d2 = faker.date_between(d1).strftime(DEFAULT_DATE_FMT)
        d1 = d1.strftime(DEFAULT_DATE_FMT)
        # Undefined Symbol
        assert self.send_request(
            {"start_date": d1, "end_date": d2, "symbol": "X"}
        ).status_code == 400

        # StartDate > EndDate
        assert self.send_request(
            {"start_date": d2, "end_date": d1, "symbol": FDFactory.rand_symb().name}
        ).status_code == 400

        # Missing Each One
        query = self.sample_query()
        for deleted in query.keys():
            assert self.send_request(
                {key: val for key, val in query.items() if key != deleted}
            ).status_code == 400

    # 404 Error
    def test_get__empty(self):
        with mock.patch("routes.get_statistics", return_value={}) as mocked:
            resp = self.send_request(self.sample_query())
            assert resp.status_code == 404
            mocked.assert_called_once()
            content = jsloads(resp.data)
            assert content["info"]["error"] != ""

    # 200 OK
    def test_get__single_ok(self):
        query = self.sample_query()
        stats = self.sample_statitstics(query['symbol'])
        with mock.patch("routes.get_statistics", return_value=stats) as mocked:
            resp = self.send_request(query)
            assert resp.status_code == 200
            mocked.assert_called_once()
            content = jsloads(resp.data)
            assert content["info"]["error"] == ""
            assert content["data"]["symbol"] == stats["symbol"] == query['symbol']
            assert content["data"]["average_daily_open_price"] == float("%.1f" % stats["average_daily_open_price"])
            assert content["data"]["average_daily_close_price"] == float("%.1f" % stats["average_daily_close_price"])
            assert content["data"]["average_daily_volume"] == float("%.1f" % stats["average_daily_volume"])
            assert content["data"]["start_date"] == query['start_date']
            assert content["data"]["end_date"] == query['end_date']
            assert len(content["data"].keys()) == 6
            assert "" == content["info"]["error"]
