from model import FinancialData, FinancialDataSerializer
from sqlalchemy.dialects.mysql import types
from sqlalchemy.sql import sqltypes
from tests.factories.financial_data import FinancialData as FDFactory
from conf.settings import DEFAULT_DATE_FMT


def test_fd_attrs():
    # id
    assert isinstance(FinancialData.id.type, types.INTEGER)
    assert not FinancialData.id.nullable

    # symbol
    assert isinstance(FinancialData.symbol.type, sqltypes.Enum)
    assert set(['AAPL', 'IBM']) == set(FinancialData.symbol.type.enums)
    assert not FinancialData.symbol.nullable

    # date
    assert isinstance(FinancialData.date.type, sqltypes.Date)
    assert not FinancialData.date.nullable

    # open_price
    assert isinstance(FinancialData.open_price.type, sqltypes.Float)
    assert not FinancialData.open_price.nullable

    # close_price
    assert isinstance(FinancialData.close_price.type, sqltypes.Float)
    assert not FinancialData.close_price.nullable

    # volume
    assert isinstance(FinancialData.volume.type, types.INTEGER)
    assert not FinancialData.volume.nullable

    # timestamps
    assert isinstance(FinancialData.created_at.type, sqltypes.DateTime)
    assert not FinancialData.created_at.nullable
    assert isinstance(FinancialData.updated_at.type, sqltypes.DateTime)
    assert not FinancialData.updated_at.nullable


def test_fd_serializer():
    fd = FDFactory.mock()
    serialized = {
        "id": fd.id,
        "symbol": fd.symbol.name,
        "date": fd.date.strftime(DEFAULT_DATE_FMT),
        "open_price": "%.1f" % fd.open_price,
        "close_price": "%.1f" % fd.close_price,
        "volume": fd.volume,
        "created_at": str(fd.created_at),
        "updated_at": str(fd.updated_at)
    }
    assert [serialized] == FinancialDataSerializer.serialize([fd])


def test_fd_serializer_with_exclusion():
    fd = FDFactory.mock()
    serialized = {
        "id": fd.id,
        "symbol": fd.symbol.name,
        "volume": fd.volume,
        "created_at": str(fd.created_at),
        "updated_at": str(fd.updated_at)
    }
    assert [serialized] == FinancialDataSerializer.serialize([fd], exclude=["date", "open_price", "close_price"])
