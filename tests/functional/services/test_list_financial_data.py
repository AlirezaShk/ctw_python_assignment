import mock
from mock import Mock
import pytest
from financial.list_financial_data import main as list_financial_data
from faker.factory import Factory
from conf.settings import DEFAULT_DATE_FMT
from tests.factories.financial_data import FinancialData as FDFactory
from lib.exceptions import PageOutofBoundsError
from flask_sqlalchemy import BaseQuery


Faker = Factory.create
faker = Faker()
faker.seed(hash(__file__))


class TestListFinancialDataService:
    def sample_query(self, page: int = 1, limit: int = 5):
        d1 = faker.date_between()
        d2 = faker.date_between(d1).strftime(DEFAULT_DATE_FMT)
        return {"start_date": d1.strftime(DEFAULT_DATE_FMT), "end_date": d2, "symbol": FDFactory.rand_symb().name, "limit": limit, "page": page}

    @mock.patch.object(BaseQuery, "count", return_value=0)
    def test_no_records(self, *args, **kwargs):
        assert list_financial_data(**self.sample_query()) == (0, [])

    @mock.patch.object(BaseQuery, "count", return_value=10)
    def test_with_records(self, *args, **kwargs):
        paginated_results = Mock()
        paginated_results.items = [FDFactory.mock() for _ in range(5)]
        with mock.patch.object(BaseQuery, "paginate", return_value=paginated_results):
            total, res = list_financial_data(**self.sample_query())
            assert total == 10
            assert len(res) == 5
            assert res[0] == paginated_results.items[0]

    @mock.patch.object(BaseQuery, "count", return_value=5)
    def test_page_oob(self, *args, **kwargs):
        paginated_results = Mock()
        paginated_results.items = [FDFactory.mock() for _ in range(5)]
        with mock.patch.object(BaseQuery, "paginate", return_value=paginated_results):
            with pytest.raises(PageOutofBoundsError):
                list_financial_data(**self.sample_query(page=2))
