import requests
from model import FinancialData
from app import cache
from .logging import Loggable
from .exceptions import SymbolUndefinedError
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from conf.settings import DEFAULT_DATE_FMT


class DailyTimeSeriesRecord:
    MAP_KEYS = {
        "open_price": "1. open",
        "close_price": "4. close",
        "volume": "6. volume"
    }

    def __init__(self, record: Dict[str, str], date: datetime, symbol: str):
        self.data = {
            "date": date,
            "updated_at": datetime.now(),
            "symbol": symbol,
            **({k: record[v] for k, v in self.MAP_KEYS.items()})
        }

    def to_model(self) -> FinancialData:
        return FinancialData(**self.data)

    def to_dict(self):
        return dict(self.data)


class AlphaVantageAPI:
    DEFAULT_FUNC = "TIME_SERIES_DAILY_ADJUSTED"
    VALID_SYMBOLS = FinancialData.Symbols
    DEPRECATION_LIMIT_DAYS = 14
    FUNC_DATA_KEY = {"TIME_SERIES_DAILY_ADJUSTED": "Time Series (Daily)"}

    def __init__(self, api_key: str, func: Optional[str] = DEFAULT_FUNC):
        self.api_key = api_key
        self.func = func

    @Loggable("AlphaVantageAPI")
    def _get_daily_data_json(self, symbol_code: str) -> str:
        url = f'https://www.alphavantage.co/query?function={self.func}&datatype=json&symbol={symbol_code}&outputSize=compact&apikey={self.api_key}'
        return requests.get(url).json()

    @cache.memoize(60)
    def _standardize_symbol(self, symbol: str) -> str:
        try:
            return self.VALID_SYMBOLS[symbol].name
        except KeyError:
            if symbol not in self.VALID_SYMBOLS.as_set():
                raise SymbolUndefinedError(symbol=symbol)
            else:
                return symbol.name

    @Loggable("AlphaVantageAPI")
    def get_biweekly_data(self, symbol: str) -> List[FinancialData]:
        symbol_code = self._standardize_symbol(symbol)
        time_series_data = self._get_daily_data_json(symbol_code)[self.FUNC_DATA_KEY[self.func]]
        date_cursor = datetime.now()
        res = []
        parser = self._get_parser()
        for i in range(self.DEPRECATION_LIMIT_DAYS):
            key = date_cursor.strftime(DEFAULT_DATE_FMT)
            try:
                res.append(
                    parser(record=time_series_data[key],
                           date=date_cursor, symbol=symbol_code).to_dict()
                )
            except KeyError: pass
            date_cursor -= timedelta(days=1)
        return res

    @cache.cached(60, key_prefix="vantage_data_parser/%s")
    def _get_parser(self) -> type:
        match self.func:
            case "TIME_SERIES_DAILY_ADJUSTED":
                return DailyTimeSeriesRecord
            case _:
                raise BaseException
