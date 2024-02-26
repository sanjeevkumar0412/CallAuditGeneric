from db_configuration import Base,db,app,TableBase
from sqlalchemy.ext.automap import automap_base
from flask import flash
from db_connection import DbConnection

# from flask import flash

# Fetch for All Record
class DBRecord:
    _instance = None    
    table_list = Base.classes.keys()         
            
    def __init__(self):
         self.db_instance = DbConnection.get_instance()
        # raise RuntimeError('Error on DBRecord Call get_instance() instead')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def get_all_record(self,table_name):
        try:
            # db.session.close_all()
            # db.session.close()
            # flash('Loadin data for all records')
            # db.session.close()
            # engine_obj = db.get_engine(app)
            # engine_obj.dispose()
            with app.app_context():              
                table_class = Base.classes[table_name]
                column_names=TableBase.metadata.tables[table_name].columns.keys()
                data = db.session.query(table_class).all()
                print('Query Data -------------------',data)
                # print(111111111,data)
                result = []
                for client in data:
                    column_values = {column: getattr(client, column) for column in column_names}
                    result.append(column_values)
                return {'data': result}
        except Exception as e:
             print(".........Error in get_all_record...........",e)
             DbConnection.close_database_connection()
           

# Fetch Single Record based on id

    def get_single_record(table_name, id):
        with app.app_context():
            table_class = Base.classes[table_name]
            print("Base",table_class)
            data_check  = db.session.query(table_class).all()
            if len(data_check) > 0:
                column_by_id = db.session.query(table_class).get(id)
                # column_by_id = db.session.query(table_class).filter_by(clientid=id).first()
                if column_by_id ==None:
                    data ={"message":"Record not found for this ID:: "+ str(id)}
                else:
                    column_names = TableBase.metadata.tables[table_name].columns.keys()
                    data = {column: getattr(column_by_id, column) for column in column_names}
            else:
                data ={"message":"Record not available for this table"+table_name}

        return {'data': data}

    # print("55555555555",get_single_record("client))
    #Delete Record from id

    def delete_single_record(table_name,id):
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