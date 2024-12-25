import logging
from abc import ABC, abstractmethod
import os
from cfg.config import LOG_PATH, RELATIVE_PATH


class Handler(ABC):
    def __init__(self, logger, log_file):
        self.__path = RELATIVE_PATH+"/"+LOG_PATH
        os.makedirs(self.__path, exist_ok=True)
        self._logger = logger
        # stop propagating to root logger
        self._logger.propagate = False
        self._log_file = log_file

    @abstractmethod
    def log_to_file(self, log_msg):
        pass

    def _add_handler(self):
        _handler = logging.FileHandler(os.path.join(self.__path, self._log_file))
        _handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        self._logger.addHandler(_handler)