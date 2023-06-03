from app import app as application, db, api, cache
from conf.settings import DEBUG, APP_PORT
from routes import api as ns

api.add_namespace(ns)

with application.app_context():
    cache.init_app(application)
    db.initialize()

if __name__ == '__main__':
    application.run(debug=DEBUG, use_reloader=True, host="0.0.0.0", port=APP_PORT)
