"""
The FinancialData model represents the stock market data, founded on: https://www.alphavantage.co/documentation

The defined symbols are: IBM, AAPL
"""

from app import db, cache
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.schema import UniqueConstraint
import enum
from sqlalchemy import Enum
from typing import Set, List, Dict, Any, Optional
from conf.settings import DEFAULT_DATE_FMT
from lib.exceptions import SymbolUndefinedError

db_core = db.core


class FinancialData(db_core.Model):
    """Represents a stock market data.

    Table: `financial_data`
    PK: id (BigInt, AutoInc)
    Index:
        - PK
        - Unique Constraint on (`symbol`, `date`)
    Validates:
        - `symbol`
    """
    __tablename__ = 'financial_data'
    __table_args__ = (UniqueConstraint('symbol', 'date', name='unique_symbol_per_date_index'),)

    class Symbols(enum.Enum):
        AAPL = 'APPLE'
        IBM = 'IBM'

        @classmethod
        @cache.memoize(50)
        def as_set(cls, codes_only: bool = False) -> Set:
            res = set(cls)
            if codes_only:
                res = set(map(lambda x: x.name, res))
            return res

    id = db_core.Column(INTEGER(unsigned=True), primary_key=True)
    symbol = db_core.Column(Enum(Symbols, create_constraint=True), nullable=False, index=True)
    date = db_core.Column(db_core.Date(), nullable=False, index=True)
    open_price = db_core.Column(db_core.Float(precision=2), nullable=False)
    close_price = db_core.Column(db_core.Float(precision=2), nullable=False)
    volume = db_core.Column(INTEGER(unsigned=True), nullable=False)
    created_at = db_core.Column(db_core.DateTime(timezone=True),
                                server_default=func.now(), nullable=False)
    updated_at = db_core.Column(db_core.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f'<FinancialData id={self.id}>'

    @classmethod
    def as_sql_table(cls, only_required=True):
        keys = set(cls.__table__.columns.keys())
        if only_required:
            keys.discard("id")
            keys.discard("created_at")
            keys = list(keys)
            return f"`{cls.__tablename__}` ({', '.join(keys)})", keys
        keys = list(keys)
        return f"`{cls.__tablename__}` ({', '.join(keys)})", keys

    def __eq__(self, other: object):
        return (self.id == other.id is not None) or (
            self.id == other.id and
            self.symbol == other.symbol and
            self.date == other.date and
            self.open_price == other.open_price and
            self.close_price == other.close_price and
            self.volume == other.volume
        )

    @validates("symbol")
    def _validate_symbol(self, key, symb):
        self.is_symbol_valid(symb)
        return symb

    @classmethod
    def is_symbol_valid(cls, symb):
        if symb not in cls.Symbols.as_set(codes_only=True) and symb not in cls.Symbols.as_set():
            raise SymbolUndefinedError(symb)

    def to_dict(self, all_str: Optional[bool] = True):
        res = dict(self.__dict__)
        # Addtional SQLAlchemy Model attribute
        del res["_sa_instance_state"]
        if all_str:
            if not isinstance(res["symbol"], str):
                res["symbol"] = res["symbol"].name
        return res


class FinancialDataSerializer:
    @classmethod
    def serialize(cls, objs: List[FinancialData], exclude: List[str] = []) -> List[Dict[str, Any]]:
        return list(map(lambda x: cls.transform(x, exclude), objs))

    @staticmethod
    def transform(o: object, exclude: List[str]) -> Dict[str, Any]:
        res = {
            "id": o.id,
            "symbol": o.symbol.name,
            "date": o.date.strftime(DEFAULT_DATE_FMT),
            "open_price": "%.1f" % o.open_price,
            "close_price": "%.1f" % o.close_price,
            "volume": o.volume,
            "created_at": str(o.created_at),
            "updated_at": str(o.updated_at)
        }
        for attr in exclude:
            del res[attr]
        return res
