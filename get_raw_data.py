from lib.exceptions import ApiKeyNotFound
from lib.avantage_api import AlphaVantageAPI
from app import db, app as application


def get_api_key():
    try:
        with open("conf/api_key", "r") as f:
            return f.read()
    except FileNotFoundError:
        raise ApiKeyNotFound


API_KEY = get_api_key()
client = AlphaVantageAPI(api_key=API_KEY)

with application.app_context():
    for symbol in AlphaVantageAPI.VALID_SYMBOLS:
        client.getBiWeeklyData(symbol, callback=db.enqueue)
        db.commit()
