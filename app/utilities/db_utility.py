from services.logger import Logger
from db_connection import DbConnection
from services.logger_service import LoggerService


class DBUtility:
   _instance = None

   def __init__(self):
        self.logger = Logger()
        self.logger_service = LoggerService()
        self.db_connection = DbConnection()

   def __new__(cls):
       if cls._instance is None:
           cls._instance = super().__new__(cls)
       return cls._instance


   def get_logger_info(self):
       self.logger_service.info('calling DBUtility')