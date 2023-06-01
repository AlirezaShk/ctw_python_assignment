from app import db
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.schema import UniqueConstraint
import enum
from sqlalchemy import Enum


db_core = db.conn


class FinancialData(db_core.Model):
    __tablename__ = 'financial_data'
    __table_args__ = (UniqueConstraint('symbol', 'date', name='unique_symbol_per_date_index'),)

    class Symbols(enum.Enum):
        APPLE = 'AAPL'
        IBM = 'IBM'

        @classmethod
        def as_set(cls):
            return set(cls)

    id = db_core.Column(INTEGER(unsigned=True), primary_key=True)
    symbol = db_core.Column(Enum(Symbols), nullable=False, index=True)
    date = db_core.Column(db_core.Date(), nullable=False, index=True)
    open_price = db_core.Column(db_core.Float(precision=2), nullable=False)
    close_price = db_core.Column(db_core.Float(precision=2), nullable=False)
    volume = db_core.Column(INTEGER(unsigned=True), nullable=False)
    created_at = db_core.Column(db_core.DateTime(timezone=True),
                                server_default=func.now())

    def __repr__(self):
        return f'<FinancialData id={self.id}>'
