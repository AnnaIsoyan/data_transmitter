import logging
from cfg.config import SUCCESS_LOG_FILE_NAME
from handler.Handler import Handler

class SuccessHandler(Handler, logging.Handler):
    def __init__(self, success_logger):
       super().__init__(success_logger, SUCCESS_LOG_FILE_NAME+'.log')
       self._logger.setLevel(logging.INFO)
       self._add_handler()

    def log_to_file(self, log_msg):
        self._logger.info(log_msg)