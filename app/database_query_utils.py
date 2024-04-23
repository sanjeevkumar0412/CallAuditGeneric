from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from db_layer.models import AudioTranscribe
from sqlalchemy.sql import select
from app.utilities.utility import GlobalUtility
from app.services.logger import Logger
from app.configs.error_code_enum import *


class DBRecord:
    _instance = None

    def __init__(self):
        self.global_utility = GlobalUtility()
        self.logger = Logger()
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    def get_sql_cursor(self,dns_string):
        engine = create_engine(dns_string)
        inspector = Inspector.from_engine(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.raw_connection()
        cursor = conn.cursor()
        all_tables = inspector.get_table_names()
        return cursor, all_tables
    def list_of_dictionary_conversion(self,cursor):
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

    def get_all_record_by_proc(self, server_name, database_name, client_id,table_name):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            try:
                session = self.global_utility.get_database_session(connection_string)
                logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    raw_sql = f"SELECT * FROM {table}"
                    cursor.execute(raw_sql)
                    result = self.list_of_dictionary_conversion(cursor)
                    if len(result) > 0:
                        api_object = self.global_utility.get_json_format(result,SUCCESS)
                        return api_object,SUCCESS
                    else:
                        api_object = self.global_utility.get_json_format(result,RESOURCE_NOT_FOUND,True,'There is no record in the database'),RESOURCE_NOT_FOUND
                        return api_object
                else:
                    api_object = {
                        "result": [],
                        "message": f"Table {table_name} not found ! ",
                        "status": 'failure',
                        'status_code': RESOURCE_NOT_FOUND
                    }
                    return api_object,RESOURCE_NOT_FOUND
            except Exception as e:
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code': INTERNAL_SERVER_ERROR
                }
                return api_object,INTERNAL_SERVER_ERROR
            finally:
                self.logger.log_entry_into_sql_table(session,client_id, True,logger_handler)
                cursor.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR
    def get_all_record(self, server_name, database_name, client_id,table_name):
        from datetime import datetime
        print("Start get_all_record / connection_string time:-", datetime.now())
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        print("End connection_string time:-", datetime.now())
        if len(connection_string) > 0:
            try:
                print("Start Table Data time:-", datetime.now())
                session = self.global_utility.get_database_session(connection_string)
                # logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    raw_sql = f"SELECT * FROM {table}"
                    cursor.execute(raw_sql)
                    result = self.list_of_dictionary_conversion(cursor)
                    print("End Table Data time:-", datetime.now())
                    if len(result) > 0:
                        api_object = self.global_utility.get_json_format(result,SUCCESS)
                        return api_object,SUCCESS
                    else:
                        api_object = self.global_utility.get_json_format(result,RESOURCE_NOT_FOUND,True,'There is no record in the database'),RESOURCE_NOT_FOUND
                        return api_object
                else:
                    api_object = {
                        "result": [],
                        "message": f"Table {table_name} not found ! ",
                        "status": 'failure',
                        'status_code': RESOURCE_NOT_FOUND
                    }
                    return api_object,RESOURCE_NOT_FOUND
            except Exception as e:
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code': INTERNAL_SERVER_ERROR
                }
                return api_object,INTERNAL_SERVER_ERROR
            finally:
                # self.logger.log_entry_into_sql_table(session,client_id, True,logger_handler)
                cursor.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR


    def get_record_by_id(self, server_name, database_name, client_id,table_name, id):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            try:
                session = self.global_utility.get_database_session(connection_string)
                logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    raw_sql = f"SELECT * FROM  {table_name} WHERE Id = {id}"
                    cursor.execute(raw_sql)
                    result = self.list_of_dictionary_conversion(cursor)
                    result = {"status": SUCCESS, "result": result},SUCCESS
                else:
                    result = {"status": RESOURCE_NOT_FOUND, "Info": f"Table {table_name} not found !"},RESOURCE_NOT_FOUND

                if result == []:
                    result = {"status": RESOURCE_NOT_FOUND, "Info": f"Information is not available for {table_name} Id {id} !"},RESOURCE_NOT_FOUND

                return {'data': result}
            except Exception as e:
                self.logger.error(".........Error in get_record_by_id...........", str(e))
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code': INTERNAL_SERVER_ERROR
                }
                return api_object, INTERNAL_SERVER_ERROR
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def get_data_by_column_name(self,server_name, database_name, client_id, table_name, column_name, column_value):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            try:
                session = self.global_utility.get_database_session(connection_string)
                logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables,inspector = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    check_column = inspector.get_columns(table_name)
                    column_exists = any(column['name'] == column_name for column in check_column)
                    if column_exists:
                        raw_sql = f"SELECT * FROM {table_name} WHERE {column_name} = '{column_value}'"
                        cursor.execute(raw_sql)
                        result = self.list_of_dictionary_conversion(cursor)
                        api_object = {
                            "result": result,
                            "message": 'The data result set that the service provided.',
                            "status": 'success',
                            'status_code': SUCCESS
                        }
                        return api_object,SUCCESS
                    else:
                        api_object = {
                            "result": [],
                            "message": f"Column  {column_name} not found!",
                            "status": 'failure',
                            'status_code': RESOURCE_NOT_FOUND
                        }
                        return api_object,RESOURCE_NOT_FOUND
                else:
                    api_object = {
                        "result": [],
                        "message": f"Column  {column_name} not found!",
                        "status": 'failure',
                        'status_code': RESOURCE_NOT_FOUND
                    }
                    return api_object,RESOURCE_NOT_FOUND
            except Exception as e:
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code': INTERNAL_SERVER_ERROR
                }
                return api_object,INTERNAL_SERVER_ERROR
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def update_record_by_column(self,server_name, database_name, client_id, table_name, column_to_update, new_value, condition_column, condition_value):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            try:
                session = self.global_utility.get_database_session(connection_string)
                logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables,inspector = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    check_column = inspector.get_columns(table_name)
                    column_exists = any(column['name'] == column_to_update for column in check_column)
                    if column_exists:
                        raw_sql = f"UPDATE {table_name} SET {column_to_update} = '{new_value}' WHERE {condition_column} = '{condition_value}'"
                        cursor.execute(raw_sql)
                        result = {"status":SUCCESS, "msg": f"Successfully updated the record"},SUCCESS
                    else:
                        result = {"status": RESOURCE_NOT_FOUND, "Info": f"Column  {column_to_update} not found!"},RESOURCE_NOT_FOUND
                else:
                    result = {"status": RESOURCE_NOT_FOUND, "Info": f"Table {table_name} not found !"},RESOURCE_NOT_FOUND

                return {'data': result}
            except Exception as e:
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code': INTERNAL_SERVER_ERROR
                }
                return api_object,INTERNAL_SERVER_ERROR
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def delete_record_by_id(self, server_name, database_name, client_id,table_name, id):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            try:
                session = self.global_utility.get_database_session(connection_string)
                logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
                cursor, all_tables = self.get_sql_cursor(connection_string)
                table = self.global_utility.get_table_name(all_tables, table_name)
                if table is not None:
                    raw_sql = f"DELETE FROM  {table_name} WHERE Id = {id}"
                    cursor.execute(raw_sql)
                    result = {"status": SUCCESS, "msg": f"Successfully deleted record {id}"},SUCCESS
                else:
                    result = {"status": RESOURCE_NOT_FOUND, "Info": f"Table {table_name} not found !"},RESOURCE_NOT_FOUND

                return {'data': result}
            except Exception as e:
                api_object = {
                    "result": [],
                    "message": str(e),
                    "status": 'failure',
                    'status_code':INTERNAL_SERVER_ERROR
                }
                return api_object,INTERNAL_SERVER_ERROR
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def get_master_data_by_id(self,server_name, database_name, client_id, table_name, id):
        try:
            connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
            cursor, all_tables = self.get_sql_cursor(connection_string)
            table = self.global_utility.get_table_name(all_tables, table_name)
            if table is not None:
                combined_filter = AudioTranscribe.ClientId = id
                query = select([AudioTranscribe]).where(combined_filter)
                raw_sql = f"SELECT * FROM  AudioTranscribe WHERE ClientId = {id}"
                cursor.execute(raw_sql)
                result = self.list_of_dictionary_conversion(cursor)
                result = {"status": "200", "result": result}
            else:
                result = {"status": "404", "Info": f"Table {table_name} not found !"}

            if result == []:
                result = {"status": '204', "Info": f"Information is not available for {table_name} Id {id} !"}

            return {'data': result}
        except Exception as e:
            api_object = {
                "result": [],
                "message": e,
                "status": 'failure',
                'status_code': 500
            }
            return api_object
