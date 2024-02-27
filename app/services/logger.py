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
        # self._logs += f"[DEBUG] {message}\n"
        logger.error(f"Debug message : {message}")

    def info(self, message):
        # self._logs += f"[INFO] {message}\n"
        logger.error(f"Logger Info : {message}")

    def warning(self, message):
        # self._logs += f"[WARNING] {message}\n"
        logger.error(f"Warning message  : {message}")

    def error(self, function_name,message):
        # self._logs += f"[ERROR] {message}\n"
        logger.error(f"Error in {function_name} : {message}")

    def get_logs(self,message):
        print(self._logs)
        # logger.log(f"Log message : {message}")
    
    def log_exceptions(self,function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                logger.exception(f"An error occurred in {function.__name__}: {e}")   
                """
                # Example usage Decorator  :
                    @log_exceptions
                    def divide(a, b):
                        return a / b
                """            
        return wrapper