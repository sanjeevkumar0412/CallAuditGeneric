from db_connection import DbConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.engine.reflection import Inspector

dns = f'mssql+pyodbc://FLM-VM-COGAIDEV/AudioTrans?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(dns)
inspector = Inspector.from_engine(engine)
Session = sessionmaker(bind=engine)

session = Session()
conn = engine.raw_connection()
cursor = conn.cursor()

tables_check = inspector.get_table_names()
class DBRecord:
    _instance = None

    def __init__(self):
        self.db_instance = DbConnection()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def list_of_dictionary_conversion(self):
        from datetime import datetime
        res = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            # Convert datetime objects to strings
            for key, value in row_dict.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            res.append(row_dict)
        return res

    def get_all_record(self,table_name):
        try:
            # with app.app_context():
            # raw_sql = 'SELECT * FROM '+'dbo.'+table_name
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"SELECT * FROM {table_name}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion()
                print("DDD",result)
            else:
                result = {"Info": f"Invalid Table name  {table_name} !"}

            if result==[]:
                result={"Info":f"Data is not available for {table_name} !"}
            return {'data': result}
        except Exception as e:
            # DbConnection.close_database_connection()
            print(".........Error in get_all_record...........", e)

    def get_record_by_id(self,table_name, id):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"SELECT * FROM  {table_name} WHERE Id = {id}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion()
            else:
                result = {"Info": f"Invalid Table name  {table_name} !"}

            if result==[]:
                result={"Info":f"Information is not available for {table_name} Id {id} !"}

            return {'data': result}
        except Exception as e:
            # DbConnection.close_database_connection()
            print(".........Error in get_record_by_id...........", e)

    def get_data_by_column_name(self, table_name, column_name,column_value):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                check_column = inspector.get_columns(table_name)
                column_exists = any(column['name'] == column_name for column in check_column)
                if column_exists:
                    raw_sql =  f"SELECT * FROM {table_name} WHERE {column_name} = '{column_value}'"
                    cursor.execute(raw_sql)
                    result = self.list_of_dictionary_conversion()
                else:
                    result = {"Info": f"Invalid Column name  {column_name} !"}
            else:
                result = {"Info": f"Invalid Table name  {table_name} !"}

            if result==[]:
                result={"Info":f"Data is not available for {table_name} !"}
            return {'data': result}
        except Exception as e:
            print("Error function in get_data_by_column_name",e)

    def delete_record_by_id(self, table_name, id):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"DELETE FROM  {table_name} WHERE Id = {id}"
                cursor.execute(raw_sql)
                result={"msg":f"Successfully deleted record {id}"}
            else:
                result = {"Info": f"Invalid Table name  {table_name} !"}

            return {'data': result}
        except Exception as e:
            print("Error: delete_single_record",e)