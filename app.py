from flask import Flask, g
from flask_restful import Api
from handler import SuccessHandler, ErrorHandler
from sources import ReceiveDataTransmitter, HealthCheck, DownloadFile, SendDataTransmitter
from cfg import APP_HOST, APP_PORT, APP_PORT_DEBUG, DEBUG_MODE
from scheduler import SendDataScheduler
import logging

_scheduler = SendDataScheduler()
_scheduler.start_interval_scheduler(minutes=1)

success_logger = logging.getLogger("my_success_logger")
error_logger = logging.getLogger("my_error_logger")


def initialize_handlers(current_app):
    @current_app.before_request
    def initialize_error_handlers():
        if success_logger.hasHandlers():
            success_logger.handlers = []
        if error_logger.hasHandlers():
            error_logger.handlers = []
        g.success_handler = SuccessHandler(success_logger)
        g.error_handler = ErrorHandler(error_logger)


app = Flask(__name__)

''''@app.errorhandler(Exception)
def handle_exception(e):
    return 'bad request!', 400'''

initialize_handlers(app)

api = Api(app)

api.add_resource(HealthCheck, "/")
api.add_resource(ReceiveDataTransmitter, "/exchange/submit")

api.add_resource(DownloadFile, "/download/<unique_id>")
api.add_resource(SendDataTransmitter, "/send_out")

if __name__ == "__main__":
    app.run(host=APP_HOST, debug=DEBUG_MODE, port=APP_PORT)
