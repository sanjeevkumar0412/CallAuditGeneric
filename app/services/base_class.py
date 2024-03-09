from loguru import logger

class BaseClass:

    _instance = None
    _logs = ""

    def __init__(self):
        raise RuntimeError('Error on BaseClass Call get_instance() instead')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    