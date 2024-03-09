# from dependency_injector import containers, providers, dependencies
from loguru import logger
from pathlib import Path


class LoggerService:
    _instance = None
    _logs = ""

    def __init__(self):
        self._instance = logger
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def debug(self, message: str):
        logger.debug(f"Debug message : {message}")

    def info(self, message):
        logger.info(f"Logger Info : {message}")

    @staticmethod
    def warning(self, message):
        logger.warning(f"Warning message  : {message}")

    def error(self, function_name, message):
        logger.error(f"Error in {function_name} : {message}")

    @staticmethod
    def get_logs(self, message):
        logger.log(f"Log message : {message}")

    def log_exceptions(self, function):
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

    def custom_catch(self, *args, **kwargs):
        try:
            return super().catch(*args, **kwargs)
            """
                # Replace the default logger with the custom logger
                self.logger.remove()
                self.logger.add(self.logger.custom_catch(), format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
                # Test the custom logger
                logger.info("This is an information message")
                self.logger.error("This is an error message")
            """
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.exception(f"An error occurred: {e}")

    def create_log_file(self, file_name, rotation="100 MB", level="INFO"):
        """
        Args:
            filename (str): Name of the log file to create.
            rotation (str, optional): Rotation size (e.g., "10 MB", "500 KB"). Defaults to "100 MB".
            level (str, optional): Log level. Defaults to "INFO".
        """
        logger.add(file_name, level=level, rotation=rotation)
