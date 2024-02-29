from app.db_connection import DbConnection
from app.db_configuration import Base,db,app,TableBase
from sqlalchemy.ext.automap import automap_base
from flask import flash
# from app import db_connection
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# Base = declarative_base()
# from flask import flash

# Fetch for All Record
class DBRecord:
    _instance = None
    table_list = Base.classes.keys()
    print(">>>>>>>>",table_list)


    def __init__(self):
         self.db_instance = DbConnection.get_instance()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def get_all_record(self,table_name):
        try:
            with app.app_context():
                table_class = Base.classes[table_name]
                column_names=TableBase.metadata.tables[table_name].columns.keys()
                data = db.session.query(table_class).all()
                # print(111111111111111111888888888,data)
                result = []
                for client in data:
                    column_values = {column: getattr(client, column) for column in column_names}
                    result.append(column_values)
                return {'data': result}
        except Exception as e:
            DbConnection.close_database_connection()
            print(".........Error in get_all_record...........",e)

# Fetch Single Record based on id

    def get_single_record(self,table_name, id):
        with app.app_context():
            table_class = Base.classes[table_name]
            print("Base",table_class)
            data_check  = db.session.query(table_class).all()
            print("data_check>>>>>>>>>",data_check)
            if len(data_check) > 0 or data_check !=None:
                column_by_id = db.session.query(table_class).get(id)
                # column_by_id = db.session.query(table_class).filter_by(clientid=id).first()
                if column_by_id == None:
                    data ={"message":"Record not found for this ID:: "+ str(id)}
                else:
                    column_names = TableBase.metadata.tables[table_name].columns.keys()
                    data = {column: getattr(column_by_id, column) for column in column_names}
            else:
                data ={"message":"Record not available for this table"+table_name}

        return {'data': data}

    # print("55555555555",get_single_record("client))
    #Delete Record from id

    def delete_single_record(self,table_name,id):
        with app.app_context():
            table_class = Base.classes[table_name]
            data_check  = db.session.query(table_class).all()
            if len(data_check) > 0:
                column_by_id = db.session.query(table_class).get(id)
                if column_by_id:
                    db.session.delete(column_by_id)
                    db.session.commit()
                    data = {"message": "Record successfully deleted"}
                if column_by_id == None:
                    data ={"message":"Record not found for this ID:: "+ str(id)}
            else:
                data ={"message":"Record not available !"}

        return data

    def get_data_by_column_name(self,table_name,column_value):
        with app.app_context():
            table_class = Base.classes[table_name]
            data_check  = db.session.query(table_class).all()
            if len(data_check) > 0:
                column_name = db.session.query(table_class).filter_by(username=column_value.strip()).first()
                column_class_names = TableBase.metadata.tables[table_name].columns.keys()
                data = {column: getattr(column_name, column) for column in column_class_names}
                # data = {"data": data}
        return data