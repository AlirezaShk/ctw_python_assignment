from app import app
from financial.test_api import test
import logging

logger = logging.getLogger(__name__)


def init_api():
    @app.route("/test", methods=['GET'])
    def view_test(*args):
        logger.info(args)
        return test()
