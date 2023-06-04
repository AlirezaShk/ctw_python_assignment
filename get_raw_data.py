"""Script for calling the AlphaVantageAPI and save the results to the Database.

Run the script using `python get_raw_data.py`.

Raises:
    - ApiKeyNotFoundError: If the `api_key` file is missing from `conf/api_key` path
"""
from lib.exceptions import ApiKeyNotFoundError
from lib.avantage_api import AlphaVantageAPI
from lib.logging import BasicErrorHandler
from app import db, app as application
from model import FinancialData


@BasicErrorHandler(package_name="get_raw_data", expectedErrClass=FileNotFoundError, rethrow_as=ApiKeyNotFoundError)
def get_api_key():
    with open("conf/api_key", "r") as f:
        return f.read()


def execute():
    API_KEY = get_api_key()
    client = AlphaVantageAPI(api_key=API_KEY)

    with application.app_context():
        for symbol in AlphaVantageAPI.VALID_SYMBOLS:
            db.bulk_upsert(
                cls=FinancialData,
                objects=client.get_biweekly_data(symbol)
            )


if __name__ == '__main__':
    execute()
