from app import db, cache
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.schema import UniqueConstraint
import enum
from sqlalchemy import Enum
from typing import Set

db_core = db.core


class FinancialData(db_core.Model):
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
