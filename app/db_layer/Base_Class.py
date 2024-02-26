from dependency_injector import containers, providers, dependencies
from loguru import logger
from app.db_layer.ClientTable import ClientTableClass
from app.db_layer.Transcribe_Class import TranscribeClass


class BaseClass:

    _instance = None
    _logs = ""

    def __init__(self):
        raise RuntimeError('Error on Database BaseClass Call get_instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def insert_data(self,model,model_name, data):
         self._instance.update_data(model_name,data)