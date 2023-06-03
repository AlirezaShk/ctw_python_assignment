from model import FinancialData
from sqlalchemy.dialects.mysql import types
from sqlalchemy.sql import sqltypes


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
