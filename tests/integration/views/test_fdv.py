import mock
from tests.factories.financial_data import FinancialData as FDFactory
from faker.factory import Factory
from conf.settings import DEFAULT_DATE_FMT
from . import test_client
from typing import Dict, Optional
from json import loads as jsloads


Faker = Factory.create
faker = Faker()
faker.seed(hash(__file__))


class TestFinancialDataView:
    ENDPOINT = "/api/financial_data"

    def send_request(self, query_params: Optional[Dict] = {}, path: Optional[str] = ENDPOINT):
        with test_client() as client:
            return client.get(path, query_string=query_params)

    # 400 Errors
    def test_invalid_gets(self):
        # Undefined Symbol
        assert self.send_request({"symbol": "X"}).status_code == 400
        # StartDate > EndDate
        d1 = faker.date_between()
        d2 = faker.date_between(d1).strftime(DEFAULT_DATE_FMT)
        assert self.send_request({"start_date": d2, "end_date": d1.strftime(DEFAULT_DATE_FMT)}).status_code == 400

    # 404 Error
    def test_empty_get__empty(self):
        list_res = []
        with mock.patch("routes.list_financial_data", return_value=(0, list_res)) as list_financial_data:
            resp = self.send_request()
            content = jsloads(resp.data)
            assert resp.status_code == 404
            list_financial_data.assert_called_once()
            assert content["info"]["error"] != ""

    # 200 OK
    def test_empty_get__single_ok(self):
        list_res = [FDFactory.mock()]
        with mock.patch("routes.list_financial_data", return_value=(1, list_res)) as list_financial_data:
            resp = self.send_request()
            content = jsloads(resp.data)
            assert resp.status_code == 200
            list_financial_data.assert_called_once()
            assert content["data"][0]["symbol"] == list_res[0].symbol.name
            assert content["data"][0]["open_price"] == float("%.1f" % list_res[0].open_price)
            assert content["data"][0]["close_price"] == float("%.1f" % list_res[0].close_price)
            assert content["data"][0]["volume"] == list_res[0].volume
            assert content["data"][0]["date"] == str(list_res[0].date)
            assert "created_at" not in content["data"][0]
            assert "updated_at" not in content["data"][0]
            assert "id" not in content["data"][0]
            assert content["info"]["error"] == ""
            assert content["pagination"]["count"] == 1
            assert content["pagination"]["page"] == 1
            assert content["pagination"]["pages"] == 1
            assert content["pagination"]["limit"] == 5

    # 200 OK
    def test_empty_get__collection_ok(self):
        list_res = [FDFactory.mock() for _ in range(5)]
        with mock.patch("routes.list_financial_data", return_value=(15, list_res)) as list_financial_data:
            resp = self.send_request()
            content = jsloads(resp.data)
            assert resp.status_code == 200
            list_financial_data.assert_called_once()
            assert content["data"][0]["symbol"] == list_res[0].symbol.name
            assert content["data"][0]["open_price"] == float("%.1f" % list_res[0].open_price)
            assert content["data"][0]["close_price"] == float("%.1f" % list_res[0].close_price)
            assert content["data"][0]["volume"] == list_res[0].volume
            assert content["data"][0]["date"] == str(list_res[0].date)
            assert "created_at" not in content["data"][0]
            assert "updated_at" not in content["data"][0]
            assert "id" not in content["data"][0]
            assert content["info"]["error"] == ""
            assert content["pagination"]["count"] == 15
            assert content["pagination"]["page"] == 1
            assert content["pagination"]["pages"] == 3
            assert content["pagination"]["limit"] == 5

    # 200 OK
    def test_get__collection_ok(self):
        list_res = [FDFactory.mock() for _ in range(3)]
        with mock.patch("routes.list_financial_data", return_value=(15, list_res)) as list_financial_data:
            resp = self.send_request({"limit": 3, "page": 2})
            content = jsloads(resp.data)
            assert resp.status_code == 200
            list_financial_data.assert_called_once()
            assert content["data"][0]["symbol"] == list_res[0].symbol.name
            assert content["data"][0]["open_price"] == float("%.1f" % list_res[0].open_price)
            assert content["data"][0]["close_price"] == float("%.1f" % list_res[0].close_price)
            assert content["data"][0]["volume"] == list_res[0].volume
            assert content["data"][0]["date"] == str(list_res[0].date)
            assert "created_at" not in content["data"][0]
            assert "updated_at" not in content["data"][0]
            assert "id" not in content["data"][0]
            assert content["info"]["error"] == ""
            assert content["pagination"]["count"] == 15
            assert content["pagination"]["page"] == 2
            assert content["pagination"]["pages"] == 5
            assert content["pagination"]["limit"] == 3
