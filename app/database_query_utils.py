from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from db_layer.models import AudioTranscribe
from sqlalchemy.sql import select

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

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
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

    def get_all_record(self, table_name):
        try:
            # with app.app_context():
            # raw_sql = 'SELECT * FROM '+'dbo.'+table_name
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"SELECT * FROM {table_name}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion()
                result = {"status": "200", "result": result}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found ! "}

            if result == []:
                result = {"status": '204', "Info": f"Content not available for {table_name} !"}

            return {'data': result}
        except Exception as e:
            print(".........Error in get_all_record...........", e)

    def get_record_by_id(self, table_name, id):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"SELECT * FROM  {table_name} WHERE Id = {id}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion()
                result = {"status": "200", "result": result}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            if result == []:
                result = {"status": '204', "Info": f"Information is not available for {table_name} Id {id} !"}

            return {'data': result}
        except Exception as e:
            print(".........Error in get_record_by_id...........", e)

    def get_data_by_column_name(self, table_name, column_name, column_value):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                check_column = inspector.get_columns(table_name)
                column_exists = any(column['name'] == column_name for column in check_column)
                if column_exists:
                    raw_sql = f"SELECT * FROM {table_name} WHERE {column_name} = '{column_value}'"
                    cursor.execute(raw_sql)
                    result = self.list_of_dictionary_conversion()
                    result = {"status": "200", "result": result}
                else:
                    result = {"status": "404", "Info": f"Column  {column_name} not found!"}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            if result == []:
                result = {"status": '204', "Info": f"Record not found for {table_name} !"}
            return {'data': result}
        except Exception as e:
            print("Error function in get_data_by_column_name", e)

    def update_record_by_column(self, table_name, column_to_update, new_value, condition_column, condition_value):

        try:
            table_exists = table_name in tables_check
            if table_exists:
                check_column = inspector.get_columns(table_name)
                column_exists = any(column['name'] == column_to_update for column in check_column)
                if column_exists:
                    raw_sql = f"UPDATE {table_name} SET {column_to_update} = '{new_value}' WHERE {condition_column} = '{condition_value}'"
                    cursor.execute(raw_sql)
                    result = {"status": '200', "msg": f"Successfully updated the record"}
                else:
                    result = {"status": "404", "Info": f"Column  {column_to_update} not found!"}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            return {'data': result}

        except Exception as e:
            print("Error function in update_record_by_column", e)

    def delete_record_by_id(self, table_name, id):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                raw_sql = f"DELETE FROM  {table_name} WHERE Id = {id}"
                cursor.execute(raw_sql)
                result = {"status": '200', "msg": f"Successfully deleted record {id}"}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            return {'data': result}

        except Exception as e:
            print("Error: delete_single_record", e)

    def get_master_data_by_id(self, table_name, id):
        try:
            table_exists = table_name in tables_check
            if table_exists:
                combined_filter = AudioTranscribe.ClientId = id
                query = select([AudioTranscribe]).where(combined_filter)
                raw_sql = f"SELECT * FROM  AudioTranscribe WHERE ClientId = {id}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion()
                result = {"status": "200", "result": result}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            if result == []:
                result = {"status": '204', "Info": f"Information is not available for {table_name} Id {id} !"}

            return {'data': result}
        except Exception as e:
            print(".........Error in get_record_by_id...........", e)
