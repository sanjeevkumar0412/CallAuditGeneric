from dependency_injector import containers, providers, dependencies
from loguru import logger

class ClientTableClass(object):

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
         print("insert method calling data")
         model.insert(model_name,data)

    def update_data(self,model,model_name, data):
         print("Update method calling data")