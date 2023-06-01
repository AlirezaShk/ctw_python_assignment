import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

import requests
from model import FinancialData
from .logging import Loggable
from .exceptions import SymbolUndefined
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class DailyTimeSeriesRecord:
    MAP_KEYS = {
        "open_price": "1. open",
        "close_price": "4. close",
        "volume": "6. volume"
    }

    def __init__(self, record: Dict[str, str], date: datetime, symbol: str):
        self.data = {
            "date": date,
            "symbol": symbol,
            **({k: record[v] for k, v in self.MAP_KEYS.items()})
        }

    def to_model(self) -> FinancialData:
        return FinancialData(**self.data)


class AlphaVantageAPI:
    DEFAULT_FUNC = "TIME_SERIES_DAILY_ADJUSTED"
    VALID_SYMBOLS = FinancialData.Symbols
    DEPRECATION_LIMIT_DAYS = 14
    DAILY_TIME_SERIES_KEY = "Time Series (Daily)"

    def __init__(self, api_key: str, func: Optional[str] = DEFAULT_FUNC):
        self.api_key = api_key
        self.func = func

    @Loggable("AlphaVantageAPI")
    def _getDailyDataJSON(self, symbol_code: str) -> str:
        url = f'https://www.alphavantage.co/query?function={self.func}&datatype=json&symbol={symbol_code}&outputSize=compact&apikey={self.api_key}'
        return requests.get(url).json()

    def _standardizeSymbol(self, symbol: str) -> None:
        try:
            self.VALID_SYMBOLS[symbol]
        except KeyError:
            if symbol not in self.VALID_SYMBOLS.as_set():
                raise SymbolUndefined(symbol=symbol)
            else:
                return symbol.value

    @Loggable("AlphaVantageAPI")
    def getBiWeeklyData(self, symbol: str, callback: Optional[callable] = None) -> List[FinancialData]:
        symbol_code = self._standardizeSymbol(symbol)
        time_series_data = self._getDailyDataJSON(symbol_code)[self.DAILY_TIME_SERIES_KEY]
        date_cursor = datetime.now()
        res = []
        for i in range(self.DEPRECATION_LIMIT_DAYS):
            key = date_cursor.strftime("%Y-%m-%d")
            try:
                record = DailyTimeSeriesRecord(record=time_series_data[key],
                                               date=date_cursor, symbol=symbol).to_model()
                res.append(record)
                if callback:
                    callback(record)
            except KeyError: pass
            date_cursor -= timedelta(days=1)
        return res
