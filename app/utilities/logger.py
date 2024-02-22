from loguru import logger

class AppLogger:
    def __init__(self):
        self.logger = logger.bind(classname=self.__class__.__name__)
