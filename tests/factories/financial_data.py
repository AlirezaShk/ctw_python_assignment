from model import FinancialData as OriginalModel
from .base import BaseFactory


class FinancialData(BaseFactory):
    @classmethod
    def mock(cls):
        return OriginalModel(
            id=cls.fake.pyint(),
            symbol=cls.fake.enum(OriginalModel.Symbols),
            date=cls.fake.date_between(),
            open_price=cls.fake.pyfloat(),
            close_price=cls.fake.pyfloat(),
            volume=cls.fake.pyint(),
            created_at=cls.fake.date_between(),
            updated_at=cls.fake.date_between()
        )
