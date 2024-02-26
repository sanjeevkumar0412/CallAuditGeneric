from db_configuration import Base,db,app,TableBase
from sqlalchemy.ext.automap import automap_base
table_list = Base.classes.keys()
print(table_list)
# from flask import flash

# Fetch for All Record

def get_all_record(table_name):
    with app.app_context():
        table_class = Base.classes[table_name]
        column_names=TableBase.metadata.tables[table_name].columns.keys()
        data = db.session.query(table_class).all()
        # print(111111111,data)
        result = []
        for client in data:
            column_values = {column: getattr(client, column) for column in column_names}
            result.append(column_values)
        return {'data': result}

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