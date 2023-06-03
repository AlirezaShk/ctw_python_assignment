from lib.exceptions import ApiKeyNotFoundError
from lib.avantage_api import AlphaVantageAPI
from lib.logging import BasicErrorHandler
from app import db, app as application
from model import FinancialData


@BasicErrorHandler(package_name="get_raw_data", expectedErrClass=FileNotFoundError, rethrow_as=ApiKeyNotFoundError)
def get_api_key():
    with open("conf/api_key", "r") as f:
        return f.read()


API_KEY = get_api_key()
client = AlphaVantageAPI(api_key=API_KEY)

with application.app_context():
    for symbol in AlphaVantageAPI.VALID_SYMBOLS:
        db.bulk_upsert(
            cls=FinancialData,
            attrs=client.get_biweekly_data(symbol)
        )
