import logging
from handler.Handler import Handler
from cfg.config import ERROR_LOG_FILE_NAME
from flask import abort, make_response

class ErrorHandler(Handler):
    def __init__(self, error_logger):
        super().__init__(error_logger, ERROR_LOG_FILE_NAME+'.log')
        self._logger.setLevel(logging.ERROR)
        self._add_handler()

    def log_to_file(self, log_msg):
        self._logger.error(log_msg)

    def handle_error(self, msg, code):
        abort(make_response({
            'error': 'Error',
            'message': msg
        }, code))