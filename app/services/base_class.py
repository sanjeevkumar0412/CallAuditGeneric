from dependency_injector import containers, providers, dependencies
from loguru import logger

class BaseClass(object):

    _instance = None
    _logs = ""

    def __init__(self):
        raise RuntimeError('Error on BaseClass Call get_instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    