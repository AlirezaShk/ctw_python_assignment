from app import app as application
from routes import init_api
from conf.settings import DEBUG, APP_PORT

init_api()

if __name__ == '__main__':
    application.run(debug=DEBUG, use_reloader=True, host="0.0.0.0", port=APP_PORT)
