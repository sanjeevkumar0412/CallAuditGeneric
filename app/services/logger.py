# from dependency_injector import containers, providers, dependencies
from loguru import logger

class Logger(object):

    _instance = None
    _logs = ""

    def __init__(self):
        raise RuntimeError('Error on BaseClass Call get_instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def debug(self, message):
        self._logs += f"[DEBUG] {message}\n"

    def info(self, message):
        self._logs += f"[INFO] {message}\n"

    def warning(self, message):
        self._logs += f"[WARNING] {message}\n"

    def error(self, message):
        self._logs += f"[ERROR] {message}\n"

    def get_logs(self):
        print(self._logs)