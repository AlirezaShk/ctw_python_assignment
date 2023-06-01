from app import app as application, db
from routes import init_api
from conf.settings import DEBUG, APP_PORT
from model import FinancialData

init_api()

with application.app_context():
    db.initialize()

if __name__ == '__main__':
    application.run(debug=DEBUG, use_reloader=True, host="0.0.0.0", port=APP_PORT)
