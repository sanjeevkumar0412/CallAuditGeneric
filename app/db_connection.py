from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
# from db_configuration import Base,db,app,TableBase
from app.services.logger import Logger
class DbConnection:

    _instance = None

    def __init__(self):
       self.logger = Logger.get_instance()

    @classmethod
    def get_instance(cls):
            if cls._instance is None:
                cls._instance = cls.__new__(cls)
            return cls._instance
        
    def connect_to_database(self):
        try: 
        # Connect to the database
        #     import sqlalchemy
        #     engine = sqlalchemy.create_engine('sqlite:///D:/Cogent/Cogent-AI/app/Cogent-AI.db')
        #     conn = engine.connect()
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Cogent/AI_Repo/Cogent-AI/app/Cogent-AI.db'
            db = SQLAlchemy(app)
            with app.app_context():
                Base = automap_base()
                Base.prepare(db.engine, reflect=True)
        #         Client = Base.classes.client
        except Exception as e:
            self.logger.error("connect_to_database", e)
            raise

    def close_database_connection(self):
        try:
        # Close the database connection
            print("Database connection closed")
            db.session.close()
            engine_obj = db.get_engine(app)
            engine_obj.dispose()
        except Exception as e:
            self.logger.error("close_database_connection",e)

