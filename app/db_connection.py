from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from app.db_configuration import Base,db,app,TableBase
class DbConnection:  

    _instance = None   

    def __init__(self):
        raise RuntimeError('Error on BaseClass Call get_instance() instead')

    @classmethod
    def get_instance(cls):
            if cls._instance is None:
                cls._instance = cls.__new__(cls)
            return cls._instance
        
    def connect_to_database(self):
        try: 
        # Connect to the database
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../Cogent-AI.db'
            db = SQLAlchemy(app)
            with app.app_context():
                Base = automap_base()
                Base.prepare(db.engine, reflect=True)
                Client = Base.classes.client           
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise

    def close_database_connection():
        try:
        # Close the database connection
            print("Database connection closed")
            db.session.close()
            engine_obj = db.get_engine(app)
            engine_obj.dispose()
        except Exception as e:
            print(f"Error closing the database connection: {e}")

