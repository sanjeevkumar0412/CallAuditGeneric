from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from sqlalchemy import create_engine, MetaData, Table
from app.configs.config import CONFIG
from sqlalchemy.orm import sessionmaker
import jwt
import os
import datetime
import secrets
import whisper
import time
from constants.constant import CONSTANT
from app.model.open_ai import OpenAIModel
from app.model.whisper import WhisperModel
from app.model.subprocess_model import SubProcessModel
from ldap3 import Server, Connection, ALL, SIMPLE
from db_layer.models import (Client, Configurations, Logs, FileTypesInfo, Subscriptions, AudioTranscribeTracker, \
                             AudioTranscribe, ClientMaster, AuthTokenManagement, JobStatus, SubscriptionPlan,
                             MasterConnectionString, \
                             MasterConnectionString)

global_utility = GlobalUtility()
logger = Logger()
db_connection = DbConnection()
open_ai_model = OpenAIModel()
whisper_model = WhisperModel()
sub_process_model = SubProcessModel()
# dns = f'mssql+pyodbc://FLM-VM-COGAIDEV/AudioTrans?driver=ODBC+Driver+17+for+SQL+Server'
# engine = create_engine(dns)
# Session = sessionmaker(bind=engine)
# session = Session()
# conn = engine.raw_connection()
# cursor = conn.cursor()


def get_json_format(result, status=True, message=None):
    response_message = 'The data result set that the service provided.'
    if message is not None:
        response_message = message
    api_object = {
        "result": result,
        "message": response_message,
        "status": 'success',
    }
    if not status:
        api_object = {
            "result": [],
            "message": response_message,
            "status": 'failure',
        }
    return api_object


def set_json_format(result, status=True, message=None):
    response_message = 'Record has been updated successfully..'
    if message is not None:
        response_message = message
    api_object = {
        "result": result,
        "message": response_message,
        "status": 'success',
    }
    if not status:
        api_object = {
            "result": [],
            "message": response_message,
            "status": 'failure',
        }
    return api_object

def get_database_session(connection_string):
    try:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except Exception as e:
        return get_json_format([], False, e)

def is_empty(value):
    return value is None or (isinstance(value, str) and not value.strip())


def get_all_configurations_table(server_name, database_name, client_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        # Get data from Client table
        clients_data = session.query(Client).filter_by(ClientId=client_id).all()
        client_coll = []
        for client_result in clients_data:
            client_coll.append(client_result.toDict())

        # Get data from Configuration table
        configuration_data = session.query(Configurations).filter_by(ClientId=client_id).all()
        configuration_coll = []
        for configuration_result in configuration_data:
            configuration_coll.append(configuration_result.toDict())
        filetype_info_data = session.query(FileTypesInfo).filter_by(ClientId=client_id).all()
        filetype_info_coll = []
        for status_result in filetype_info_data:
            filetype_info_coll.append(status_result.toDict())

        # Get data from Subscription table
        subscriptions_data = session.query(Subscriptions).filter_by(ClientId=client_id).all()
        subscriptions_array = []
        for subscriptions_result in subscriptions_data:
            subscriptions_array.append(subscriptions_result.toDict())

            # Get data from Job Status table
        job_status_data = session.query(JobStatus).filter_by(ClientId=client_id).all()
        job_status_coll = []
        for status_result in job_status_data:
            job_status_coll.append(status_result.toDict())

        # Get data from Subscription Plan table
        subscriptions_plan_data = session.query(SubscriptionPlan).filter_by(ClientId=client_id).all()
        subscriptions_plan_coll = []
        for subscriptions_plan_data in subscriptions_plan_data:
            subscriptions_plan_coll.append(subscriptions_plan_data.toDict())

        # global_utility.set_client_data(client_coll)
        # global_utility.set_configurations_data(configuration_coll)
        # global_utility.set_file_type_info_data(filetype_info_coll)
        # global_utility.set_subscription_data(subscriptions_array)
        # global_utility.set_job_status_data(job_status_coll)
        # global_utility.set_subscription_plan_data(subscriptions_plan_coll)
        # final_result_set =[]
        # final_result_set.append(client_coll)
        configurations = {
            'Client': client_coll,
            'Configurations': configuration_coll,
            'FileTypesInfo': filetype_info_coll,
            'Subscriptions': subscriptions_array,
            'JobStatus': job_status_coll,
            'SubscriptionsPlan': subscriptions_plan_coll
        }
        return get_json_format(configurations)
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        return get_json_format([], False, str(e))
    finally:
        session.close()


def save_log_table_entry(server_name, database):
    try:
        dns = f'mssql+pyodbc://{server_name}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        log_info = Logs(ClientId=1, LogSummary='Ldap Error', LogDetails='Ldap Error', LogType='Error',
                        ModulName='Start up process', Severity='Error')
        session.add(log_info)
        session.commit()
    except Exception as e:
        session.close()
        logger.error(f"An error occurred in save_log_table_entry: {e}")
    finally:
        session.close()


def create_audio_file_entry(session, model_info):
    record_model = model_info
    session.add(record_model)
    session.commit()
    return record_model


def update_transcribe_text(record_id, update_values, is_child_thread=True):
    try:
        db_server = global_utility.get_database_server_name()
        db_name = global_utility.get_database_name()
        model_updated = AudioTranscribe
        if is_child_thread:
            model_updated = AudioTranscribeTracker

        dns = f'mssql+pyodbc://{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        record = session.query(model_updated).get(int(record_id))
        if record is not None:  # Check if the record exists
            for column, value in update_values.items():
                setattr(record, column, value)
            # session.commit()
            print(f"Record for ID '{record_id}' updated successfully.")
        else:
            print(f"User with ID {record_id} not found.")
        session.commit()
        session.close()
    except Exception as e:
        session.close()
        logger.error(f"An error occurred in update_transcribe_text: {e}")
    finally:
        session.close()


def get_data_from_table(table_name, client_id):
    try:
        db_server = global_utility.get_database_server_name()
        db_name = global_utility.get_database_name()
        dns = f'mssql+pyodbc://{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        metadata = MetaData()
        with engine.begin() as connection:
            table = Table(table_name, metadata, autoload=False, autoload_with=engine)
            query = table.select().where(table.ClientId == client_id)
            result = connection.execute(query)
            for row in result:
                print(row)
            result.close()
    except Exception as e:
        result.close()
        logger.error(f"An error occurred in update_transcribe_text: {e}")
    finally:
        result.close()


def get_audio_transcribe_table_data(server, database, client_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        audio_transcribe = session.query(AudioTranscribe).filter(
            (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != 'Completed')).all()
        audio_transcribe_array = []
        for contact in audio_transcribe:
            audio_transcribe_array.append(contact.toDict())
        return audio_transcribe_array
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        raise
    finally:
        session.close()


def get_audio_transcribe_tracker_table_data(server, database, client_id, audio_parent_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(AudioTranscribeTracker).filter(
            (AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.AudioId == audio_parent_id) & (
                    AudioTranscribeTracker.ChunkStatus != 'Completed')).all()
        print(f"Records Length :- {len(records)}")
        return records
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
    finally:
        session.close()


def update_audio_transcribe_table(server_name, database_name,client_id, record_id, update_values):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        record = session.query(AudioTranscribe).get(int(record_id))
        if record is not None:  # Check if the record exists
            for column, value in update_values.items():
                setattr(record, column, value)
            session.commit()
            return set_json_format([record_id])
        else:
            return set_json_format([], False, f"The record ID, {record_id}, could not be found.")

    except Exception as e:
        session.close()
        logger.error(f"An error occurred in update_transcribe_text: {e}")
        return set_json_format([], False, e)
    finally:
        session.close()


def update_audio_transcribe_tracker_table(server_name, database_name,client_id, record_id, update_values):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        record = session.query(AudioTranscribeTracker).get(int(record_id))
        if len(record) > 0:  # Check if the record exists
            for column, value in update_values.items():
                setattr(record, column, value)
            session.commit()
            logger.info(f"Child Record for ID '{record_id}' updated successfully.")
            record_data = session.query(AudioTranscribeTracker).filter(
                (AudioTranscribeTracker.ClientId == record.ClientId) & (
                        AudioTranscribeTracker.AudioId == record.AudioId) & (
                        AudioTranscribeTracker.ChunkStatus != 'Completed')).all()
            if len(record_data) == 0:
                parent_record = session.query(AudioTranscribe).get(int(record.AudioId))
                values = {'JobStatus': 'Drafted'}
                if record is not None:  # Check if the record exists
                    for column, value in values.items():
                        setattr(parent_record, column, value)
                    session.commit()
            return set_json_format([record_id])
        else:
            return set_json_format([], False, f"The record ID, {record_id}, could not be found.")
    except Exception as e:
        session.close()
        logger.error(f"An error occurred in update_transcribe_text: {e}")
        return set_json_format([], False, e)
    finally:
        session.close()


def get_client_configurations(server, database, client_id, master_client_user):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(Client).filter(
            (Client.ClientId == client_id) & (Client.ClientUserName == master_client_user) & (
                Client.IsActive)).all()
        print(f"Records Length :- {len(records)}")
        client_result = global_utility.get_configuration_by_column(records)
        global_utility.set_client_data(client_result)
        return client_result
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        return []
    finally:
        session.close()


def get_oauth_access_token(server, database, user_name, secret_key):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(Client).filter(
            (Client.ClientUserName == user_name) & (Client.ClientPassword == secret_key) & (
                Client.IsActive)).all()
        print(f"Records Length :- {len(records)}")
        client_result = global_utility.get_configuration_by_column(records)
        global_utility.set_client_data(client_result)
        return client_result
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        return []
    finally:
        session.close()


def get_client_master_data(server, database, client_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(ClientMaster).filter(Client.ClientId == client_id).all()
        client_result = global_utility.get_configuration_by_column(records)
        global_utility.set_master_client_data(client_result)
        return client_result
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        return []
    finally:
        session.close()


def get_ldap_authentication(server_name, database_name, client_id):
    success = True
    error_message = None
    # Establish connection with the LDAP server
    connection_string = get_connection_string(server_name, database_name, client_id)
    session = get_database_session(connection_string)
    records = session.query(Client).filter((Client.ClientId == client_id) & (Client.IsActive)).all()
    record_coll = []
    for result_elm in records:
        record_coll.append(result_elm.toDict())
    username = global_utility.get_values_from_json_array(record_coll,CONFIG.LDAP_USER_NAME)
    password = global_utility.get_values_from_json_array(record_coll,CONFIG.LDAP_USER_PASSWORD)
    server_address = global_utility.get_values_from_json_array(record_coll, CONFIG.LDAP_SERVER)

    # server_address = 'ldap://10.9.32.17:389'
    server = Server(server_address, get_info=ALL, use_ssl=False)
    try:
        # Bind to the LDAP server with provided credentials
        conn = Connection(server, user=username, password=password, authentication=SIMPLE)
        if not conn.bind():
            success = False
            error_message = str("Invalid credentials")
            return success, error_message
        # If bind is successful, credentials are valid
        success = True
        error_message = str("Credentials verified successfully")
        return success, error_message
    except Exception as e:
        success = False
        error_message = str(e)
        return success, error_message


def get_token_based_authentication(server_name, database_name, client_id, user_name):
    try:
        success = True
        error_message = None
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        record = session.query(AuthTokenManagement).filter(
            (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                Client.IsActive)).all()
        print(f"Records Length :- {len(record)}")
        if len(record) > 0:
            result = global_utility.get_configuration_by_column(record)
            token = global_utility.get_list_array_value(result,
                                                        CONFIG.TOKEN)
            record_id = global_utility.get_list_array_value(result,
                                                            CONFIG.ID)
            secret_key = global_utility.get_list_array_value(result,
                                                             CONFIG.SECRETKEY)

            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            print("Decoded token:", decoded_token)
            success = True
            error_message = str("Token verified successfully")
            return success, error_message
        else:
            generate_token(session, client_id, user_name)
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        update_token(session, record_id, user_name)
        success = True
        error_message = str("Token has expired & updated successfully.")
        return success, error_message
    except jwt.InvalidTokenError:
        success = False
        error_message = str("Invalid token")
        return success, error_message
    except Exception as e:
        success = False
        error_message = str(e)
        return success, error_message


def generate_token(session, client_id, user_name):
    try:
        secret_key = secrets.token_bytes(32)
        hex_key = secret_key.hex()
        print(f"Generated secret key: {hex_key}")
        SECRET_KEY = hex_key

        # Generate a JWT token with an expiry time of 1 hour
        payload = {
            'user_id': user_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        record_model = AuthTokenManagement(Token=token, UserName=user_name, ClientId=client_id,
                                           SecretKey=SECRET_KEY)
        session.add(record_model)
        session.commit()
        logger.info(f"Record inserted successfully. ID: {record_model.Id}")
        return record_model
        print("Generated token:", record_model.Id)
    except Exception as e:
        logger.error(f"An error occurred in update_transcribe_text: {e}")
    finally:
        session.close()


def update_token(session, record_id, user_name):
    try:
        secret_key = secrets.token_bytes(32)
        hex_key = secret_key.hex()
        print(f"Generated secret key: {hex_key}")
        SECRET_KEY = hex_key

        # Generate a JWT token with an expiry time of 1 hour
        payload = {
            'user_id': user_name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        update_values = {'Token': token, 'SecretKey': SECRET_KEY}
        record = session.query(AudioTranscribeTracker).get(int(record_id))
        if record is not None:  # Check if the record exists
            for column, value in update_values.items():
                setattr(record, column, value)
            session.commit()
        logger.info(f"Record inserted successfully. ID: {record.Id}")
        # return record
        print("Generated token:", record.Id)
    except Exception as e:
        logger.error(f"An error occurred in update_transcribe_text: {e}")
    finally:
        session.close()


def get_connection_string(server, database, client_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(MasterConnectionString).filter(
            (MasterConnectionString.ClientId == client_id) & (
                MasterConnectionString.IsActive)).all()
        record_coll = []
        for result in records:
            record_coll.append(result.toDict())
        return global_utility.get_values_from_json_array(record_coll, CONFIG.CONNECTION_STRING)
    except Exception as e:
        session.close()
        logger.error("connect_to_database", e)
        return []
    finally:
        session.close()


def get_audio_transcribe_table_data(server_name, database_name, client_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        job_status_data = session.query(JobStatus).filter(
            (JobStatus.ClientId == client_id) & (JobStatus.IsActive)).all()
        job_status_coll = []
        for status_result in job_status_data:
            job_status_coll.append(status_result.toDict())
        status_id = global_utility.get_status_by_key_name(
            job_status_coll,CONSTANT.STATUS_COMPLETED)
        results = session.query(AudioTranscribe).filter(
            (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != int(status_id))).all()
        if len(results) > 0:
            result_array = []
            for result_elm in results:
                result_array.append(result_elm.toDict())
            return get_json_format(result_array)
        elif len(results) == 0:
            return get_json_format([],True,'There is no record found in the database')
    except Exception as e:
        return get_json_format([], False, str(e))
    finally:
        session.close()

def get_audio_transcribe_tracker_table_data(server_name, database_name, client_id,audio_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        job_status_data = session.query(JobStatus).filter(
            (JobStatus.ClientId == client_id) & (JobStatus.IsActive)).all()
        job_status_coll = []
        for status_result in job_status_data:
            job_status_coll.append(status_result.toDict())
        status_id = global_utility.get_status_by_key_name(
            job_status_coll,CONSTANT.STATUS_COMPLETED)
        results = session.query(AudioTranscribeTracker).filter(
            (AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.AudioId == audio_id) & (
                    AudioTranscribeTracker.ChunkStatus != int(status_id))).all()
        if len(results) > 0:
            result_array = []
            for result_elm in results:
                result_array.append(result_elm.toDict())
            return get_json_format(result_array)
        elif len(results) == 0:
            return get_json_format([],True,'There is no record found in the database')
    except Exception as e:
        return get_json_format([], False, str(e))
    finally:
        session.close()

def get_client_master_table_configurations(server_name, database_name, client_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        results = session.query(ClientMaster).filter((ClientMaster.ClientId == client_id) & (ClientMaster.IsActive)).all()
        if len(results) > 0:
            result_array = []
            for result_elm in results:
                result_array.append(result_elm.toDict())
            return get_json_format(result_array)
        elif len(results) == 0:
            return get_json_format([],True,'There is no record found in the database')
    except Exception as e:
        return get_json_format([], False, str(e))
    finally:
        session.close()

def get_app_configurations(server_name, database_name, client_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        results = session.query(Client).filter((Client.ClientId == client_id) & (Client.IsActive)).all()
        if len(results) > 0:
            result_array = []
            for result_elm in results:
                result_array.append(result_elm.toDict())
            return get_json_format(result_array)
        elif len(results) == 0:
            return get_json_format([],True,'There is no record found in the database')
    except Exception as e:
        return get_json_format([], False, str(e))
    finally:
        session.close()

def copy_audio_files_process(server_name, database_name, client_id):
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        results_config = session.query(Configurations).filter((Configurations.ClientId == client_id) & (Configurations.IsActive)).all()
        result_config_array = []
        if len(results_config) > 0:
            for result_elm in results_config:
                result_config_array.append(result_elm.toDict())

        results_file_type = session.query(FileTypesInfo).filter((FileTypesInfo.ClientId == client_id) & (FileTypesInfo.IsActive)).all()
        result_file_type_array = []
        if len(results_file_type) > 0:
            for result_elm in results_file_type:
                result_file_type_array.append(result_elm.toDict())

        results_status = session.query(JobStatus).filter((JobStatus.ClientId == client_id) & (JobStatus.IsActive)).all()
        result_status_array = []
        if len(results_status) > 0:
            for result_elm in results_status:
                result_status_array.append(result_elm.toDict())
        if len(result_config_array) > 0:
            source_file_path = global_utility.get_configuration_by_key_name(result_config_array,CONFIG.AUDIO_SOURCE_FOLDER_PATH)
            destination_path = global_utility.get_configuration_by_key_name(result_config_array,CONFIG.AUDIO_DESTINATION_FOLDER_PATH)
            audio_file_size = int(global_utility.get_configuration_by_key_name(result_config_array,CONFIG.AUDIO_FILE_SIZE))
            is_validate_path = global_utility.validate_folder(source_file_path, destination_path)
            if is_validate_path:
                file_collection = global_utility.get_all_files(source_file_path)
                for file in file_collection:
                    file_url = source_file_path + "/" + file
                    file_name, extension = global_utility.get_file_extension(file)
                    file_type_id = global_utility.get_file_type_by_key_name(result_file_type_array, extension)
                    # if extension == ".wav" or extension == ".mp3":
                    if file_type_id > 0:
                        name_file = file_url.split('/')[-1].split('.')[0]
                        dir_folder_url = os.path.join(destination_path, name_file)
                        is_folder_created = global_utility.create_folder_structure(file, dir_folder_url,destination_path)
                        status_id = global_utility.get_status_by_key_name(result_status_array, 'PreProcessing')
                        if is_folder_created:
                            is_copied_files = global_utility.copy_file(file_url, dir_folder_url)
                            if is_copied_files:
                                audio_file_path = os.path.join(dir_folder_url, file)
                                file_size = os.path.getsize(audio_file_path)
                                file_size_mb = int(file_size / (1024 * 1024))
                                if file_size_mb > audio_file_size:
                                    logger.info(f'file {name_file} Starting with size :- {file_size}')
                                    audio_transcribe_model = AudioTranscribe(ClientId=client_id,
                                                                             AudioFileName=file, JobStatus=status_id,
                                                                             FileType=file_type_id,
                                                                             TranscribeFilePath=audio_file_path)
                                    parent_record = create_audio_file_entry(session,audio_transcribe_model)
                                    audio_chunk_process(session,client_id, parent_record,status_id,result_file_type_array, audio_file_path,
                                                                             dir_folder_url)
                                else:
                                    audio_transcribe_model = AudioTranscribe(ClientId=client_id,
                                                                             AudioFileName=file, JobStatus=status_id,
                                                                             FileType=file_type_id,
                                                                             TranscribeFilePath=audio_file_path)
                                    parent_record = create_audio_file_entry(session,audio_transcribe_model)
                                    if parent_record is not None:
                                        logger.info(f'New Item Created ID is {parent_record.Id}')
                                    chunk_transcribe_model = AudioTranscribeTracker(
                                        ClientId=client_id,
                                        AudioId=parent_record.Id,
                                        ChunkFileType=file_type_id,
                                        ChunkFileName=file, ChunkSequence=1, ChunkText='',
                                        ChunkFilePath=audio_file_path, ChunkStatus=status_id,
                                        # ChunkCreatedDate=datetime.utcnow()
                                        )
                                    child_record = create_audio_file_entry(session, chunk_transcribe_model)
                                    logger.info(f'Chunk New Item Created ID is {child_record.Id}')
                            else:
                                logger.info(f"{file} is not copied  in the destination folder {dir_folder_url}")
                                # return get_json_format([], False, f"{file} is not copied  in the destination folder {dir_folder_url}")
                        else:
                            logger.info(f"Folder is not created for the file {file}")
                            # return get_json_format([], False, f"Folder is not created for the file {file}")
                    else:
                        return get_json_format([], False, f"{file} is not supported.")
                return get_json_format([], True, "All files copied and created Successfully.")
            else:
                return get_json_format([], False, 'There is no container at the specified path.')
        else:
            return get_json_format([],False,'There is no configuration found in the table')
    except Exception as e:
        return get_json_format([], False, str(e))
    finally:
        session.close()

def audio_chunk_process(session,client_id,parent_record,status_id,result_file_type_array, audio_file_path, dir_folder_url ):
    from datetime import datetime
    chunks = global_utility.split_audio_chunk_files(audio_file_path, dir_folder_url)
    chunks_files = chunks[0]
    counter = 0
    for filename in os.listdir(dir_folder_url):
        if filename.endswith(".wav"):  # Replace ".wav" with your audio format
            counter += 1
            filepath = os.path.join(dir_folder_url, filename)
            file_name, extension = global_utility.get_file_extension(filename)
            file_type_id = global_utility.get_file_type_by_key_name(result_file_type_array, extension)
            chunk_transcribe_model = AudioTranscribeTracker(ClientId=client_id,
                                                            AudioId=parent_record.Id,
                                                            ChunkFileName=filename, ChunkSequence=counter,
                                                            ChunkText='',
                                                            ChunkFileType=file_type_id,
                                                            ChunkFilePath=filepath, ChunkStatus=status_id
                                                            # ChunkCreatedDate=datetime.utcnow()
                                                            )
            child_record = create_audio_file_entry(session,chunk_transcribe_model)
            logger.info(f'Chunk New Item Created ID is {child_record.Id}')

def update_audio_transcribe_tracker_status(session, record_id,status_id, update_values):
    # record = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.Id == record_id).all()
    # record = session.query(AudioTranscribeTracker).get(int(record_id))
    record = session.query(AudioTranscribeTracker).filter_by(Id=record_id).update(update_values)
    # record = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.Id==record_id).all()
    session.commit()
    if record > 0:  # Check if the record exists
        updated_record = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.Id == record_id).all()
        if len(updated_record) > 0:
            updated_result_array = []
            for result_elm in updated_record:
                updated_result_array.append(result_elm.toDict())
            logger.info(f"Child Record for ID '{record_id}' updated successfully.")
            record_data = session.query(AudioTranscribeTracker).filter(
                (AudioTranscribeTracker.ClientId == updated_result_array[0]['ClientId']) & (
                        AudioTranscribeTracker.AudioId == updated_result_array[0]['AudioId']) & (
                        AudioTranscribeTracker.ChunkStatus != status_id)).all()
            if len(record_data) == 0:
                values = {'JobStatus': status_id}
                parent_record = session.query(AudioTranscribe).filter_by(Id=updated_result_array[0]['AudioId']).update(values)
                session.commit()
                # if record is not None:  # Check if the record exists
                #     for column, value in values.items():
                #         setattr(parent_record, column, value)

            return set_json_format([], True, f"The record ID, {record_id} has been updated successfully.")
    else:
        return set_json_format([], False, f"The record ID, {record_id}, could not be found.")

def retries_model(failed_file,model_name):
        retries =3
        model = whisper.load_model(model_name)
        for attempt in range(retries):
            try:
                print('fialed file process start : ',failed_file)
                time.sleep(2**attempt)
                result = model.transcribe(failed_file)
                return result
                # break
            except Exception as e:
                print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")

def whisper_transcribe_audio(file_path,model_name ="base"):
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path)
        return result
    except Exception as e:
                    print(f"Error transcribing : {e}")
                    retries_model(file_path,model_name)

def retries_ai_model(client,failed_file):
        retries =3
        for attempt in range(retries):
            try:
                print('fialed file process start : ',failed_file)
                time.sleep(2**attempt)
                audio_file = open(failed_file, "rb")
                transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format='text'
                                )
                return transcript
                # break
            except Exception as e:
                print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")
def open_ai_transcribe_audio(transcribe_file, model = "whisper-1"):
    from openai import OpenAI
    client = OpenAI()
    try:
        print(' Open Ai Audio File Path',transcribe_file)
        audio_file = open(transcribe_file, "rb")
        transcript = client.audio.transcriptions.create(
                                model=model,
                                file=audio_file
                                )
        return transcript
    except Exception as e:
                    print(f"Error transcribing : {e}")
                    return retries_ai_model(client,transcribe_file)
def update_transcribe_audio_text(server_name, database_name,client_id,file_id ):
    transcript = None
    from datetime import datetime
    try:
        connection_string = get_connection_string(server_name, database_name, client_id)
        session = get_database_session(connection_string)
        results_config = session.query(Configurations).filter(
            (Configurations.ClientId == client_id) & (Configurations.IsActive)).all()
        result_config_array = []
        if len(results_config) > 0:
            for result_elm in results_config:
                result_config_array.append(result_elm.toDict())
        if len(result_config_array) > 0:
            whisper_model = global_utility.get_configuration_by_key_name(result_config_array,CONFIG.WHISPER_MODEL)
            subscriptions_model = global_utility.get_configuration_by_key_name(result_config_array,CONFIG.SUBSCRIPTION_TYPE)
            job_status_data = session.query(JobStatus).filter((JobStatus.ClientId == client_id) & (JobStatus.IsActive)).all()
            job_status_coll = []
            for status_result in job_status_data:
                job_status_coll.append(status_result.toDict())
            status_id = global_utility.get_status_by_key_name(
                job_status_coll, CONSTANT.STATUS_COMPLETED)
            audio_results = session.query(AudioTranscribeTracker).filter((AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.Id == file_id)).all()
            if len(audio_results) > 0:
                audio_result_array = []
                for result_elm in audio_results:
                    audio_result_array.append(result_elm.toDict())
                file_path = global_utility.get_values_from_json_array(audio_result_array,CONFIG.TRANSCRIBE_FILE_PATH)
                # file_path = audio_result_array[0]['ChunkFilePath']
            start_transcribe_time = datetime.utcnow()
            if subscriptions_model.lower() == CONSTANT.SUBSCRIPTION_TYPE_PREMIUM.lower():
                transcript = open_ai_transcribe_audio(file_path)
            elif subscriptions_model.lower() == CONSTANT.SUBSCRIPTION_TYPE_SMALL.lower():
                transcript = whisper_transcribe_audio(file_path,whisper_model.lower())
            elif subscriptions_model.lower() == CONSTANT.SUBSCRIPTION_TYPE_NORMAL.lower():
                transcript = whisper_transcribe_audio(file_path, whisper_model.lower())
            else:
                transcript = open_ai_model.open_ai_transcribe_large_audio(file_path, whisper_model.lower())
            end_transcribe_time = datetime.utcnow()
            update_child_values = {"ChunkText": transcript['text'], "ChunkStatus": status_id,
                                   "ChunkTranscribeStart": start_transcribe_time,
                                   "ChunkTranscribeEnd": end_transcribe_time}
            updated_result = update_audio_transcribe_tracker_status(session,file_id,status_id,update_child_values)
            return updated_result
    except Exception as e:
        return set_json_format([], False, str(e))
    finally:
        session.close()





