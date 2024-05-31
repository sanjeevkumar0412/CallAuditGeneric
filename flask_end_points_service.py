from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from sqlalchemy import create_engine
from app.configs.config import CONFIG
from app.configs.job_status_enum import JobStatusEnum
from app.configs.error_code_enum import *
from sqlalchemy.orm import sessionmaker
import jwt
import os
import datetime
import secrets
import whisper
import time
from constants.constant import CONSTANT
from app import prompt_check_list
from ldap3 import Server, Connection, ALL, SIMPLE
from db_layer.models import (Client, Configurations, FileTypesInfo, Subscriptions, AudioTranscribeTracker,
                             AudioTranscribe, ClientMaster, AuthTokenManagement, JobStatus, SubscriptionPlan,
                             AudioFileNamePattern,MasterTable,
                             MasterConnectionString,RegisterUser,LoginDetails)
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, get_jwt, decode_token
global_utility = GlobalUtility()
logger = Logger()
db_connection = DbConnection()

from openai import OpenAI
os.environ["OPENAI_API_KEY"] = prompt_check_list.open_ai_key
# os.environ["OPENAI_API_KEY"] = "Update the open AI Key here"
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


def get_json_format(result=[], status_code=200, status=True, message=None):
    response_message = 'The data result set that the service provided.'
    if message is not None:
        response_message = message
    api_object = {
        "result": result,
        "message": response_message,
        "status": 'success',
        'status_code': status_code
    }
    if not status:
        api_object = {
            "result": result,
            "message": response_message,
            "status": 'failure',
            'status_code': status_code
        }
    return api_object


def set_json_format(result=[], status_code=200, status=True, message=None):
    response_message = 'Record has been updated successfully..'
    if message is not None:
        response_message = message
    api_object = {
        "result": result,
        "message": response_message,
        "status": 'success',
        'status_code': status_code
    }
    if not status:
        api_object = {
            "result": result,
            "message": response_message,
            "status": 'failure',
            'status_code': status_code
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


def get_all_configurations_table(server_name, database_name, client_id,user_name):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
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
                job_status_data = session.query(JobStatus).filter(JobStatus.IsActive).all()
                job_status_coll = []
                for status_result in job_status_data:
                    job_status_coll.append(status_result.toDict())

                # Get data from Subscription Plan table
                subscriptions_plan_data = session.query(SubscriptionPlan).filter_by(ClientId=client_id).all()
                subscriptions_plan_coll = []
                for subscriptions_plan_data in subscriptions_plan_data:
                    subscriptions_plan_coll.append(subscriptions_plan_data.toDict())

                configurations = {
                    'Client': client_coll,
                    'Configurations': configuration_coll,
                    'FileTypesInfo': filetype_info_coll,
                    'Subscriptions': subscriptions_array,
                    'JobStatus': job_status_coll,
                    'SubscriptionsPlan': subscriptions_plan_coll
                }
                return get_json_format(configurations,SUCCESS),SUCCESS
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']

        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False,
                           str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        logger.error("connect_to_database", str(e))
        return get_json_format([],INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def create_audio_file_entry(session, model_info):
    record_model = model_info
    session.add(record_model)
    session.commit()
    return record_model


def get_audio_transcribe_table_data(server, database, client_id):
    try:
        completed_status = JobStatusEnum.CompletedTranscript
        status_id = completed_status.value
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger_handler = logger.log_entry_into_sql_table(session, client_id, False)
        audio_transcribe = session.query(AudioTranscribe).filter(
            (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != status_id)).all()
        audio_transcribe_array = []
        for contact in audio_transcribe:
            audio_transcribe_array.append(contact.toDict())
        return audio_transcribe_array
    except Exception as e:
        session.close()
        logger.error("connect_to_database", str(e))
        raise
    finally:
        logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        session.close()


def get_audio_transcribe_tracker_table_data(server, database, client_id, audio_parent_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger_handler = logger.log_entry_into_sql_table(session, client_id, False)
        records = session.query(AudioTranscribeTracker).filter(
            (AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.AudioId == audio_parent_id) & (
                    AudioTranscribeTracker.ChunkStatus != 'Completed')).all()
        print(f"Records Length :- {len(records)}")
        return records
    except Exception as e:
        session.close()
        logger.error("connect_to_database", str(e))
    finally:
        logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        session.close()


def update_audio_transcribe_table(server_name, database_name, client_id,user_name, record_id, update_values):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                record = session.query(AudioTranscribe).get(int(record_id))
                if record is not None:  # Check if the record exists
                    for column, value in update_values.items():
                        setattr(record, column, value)
                    session.commit()
                    return set_json_format([record_id],SUCCESS),SUCCESS
                else:
                    return set_json_format([],INTERNAL_SERVER_ERROR, False, f"The record ID, {record_id}, could not be found."),INTERNAL_SERVER_ERROR
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False,
                                   str(connection_string['message'])), RESOURCE_NOT_FOUND

    except Exception as e:
        session.close()
        logger.error(f"An error occurred in update_transcribe_text: {e}",str(e))
        return set_json_format([],INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def update_audio_transcribe_tracker_table(server_name, database_name, client_id,user_name, record_id, update_values):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                record = session.query(AudioTranscribeTracker).get(int(record_id))
                if len(record) > 0:  # Check if the record exists
                    for column, value in update_values.items():
                        setattr(record, column, value)
                    session.commit()
                    logger.info(f"Id—the {record_id} record in the AudioTranscribeTracker Table has been successfully updated.")
                    record_data = session.query(AudioTranscribeTracker).filter(
                        (AudioTranscribeTracker.ClientId == record.ClientId) & (
                                AudioTranscribeTracker.AudioId == record.AudioId) & (
                                AudioTranscribeTracker.ChunkStatus != 'Completed')).all()
                    if len(record_data) == 0:
                        parent_record = session.query(AudioTranscribe).get(int(record.AudioId))
                        status_draft = JobStatusEnum.Draft
                        status_id = status_draft.value
                        values = {'JobStatus': status_id}
                        if record is not None:  # Check if the record exists
                            for column, value in values.items():
                                setattr(parent_record, column, value)
                            session.commit()
                    return set_json_format([record_id],SUCCESS),SUCCESS
                else:
                    return set_json_format([],INTERNAL_SERVER_ERROR, False, f"The record ID, {record_id}, could not be found."),INTERNAL_SERVER_ERROR
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False,
                                   str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        session.close()
        logger.error(f"An error occurred in update_transcribe_text: ",str(e))
        return set_json_format([],INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, False,logger_handler)
        session.close()
        session_logger.close()


def get_client_configurations(server, database, client_id, master_client_user):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger_handler = logger.log_entry_into_sql_table(session, client_id, False)
        records = session.query(Client).filter(
            (Client.ClientId == client_id) & (Client.ClientUserName == master_client_user) & (
                Client.IsActive)).all()
        print(f"Records Length :- {len(records)}")
        client_result = global_utility.get_configuration_by_column(records)
        global_utility.set_client_data(client_result)
        return client_result
    except Exception as e:
        logger.error("connect_to_database", str(e))
        return []
    finally:
        logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
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
        logger.error("connect_to_database", str(e))
        return []
    finally:
        session.close()


def get_client_master_data(server, database, client_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger_handler = logger.log_entry_into_sql_table(session, client_id, False)
        records = session.query(ClientMaster).filter(Client.ClientId == client_id).all()
        client_result = global_utility.get_configuration_by_column(records)
        global_utility.set_master_client_data(client_result)
        return client_result
    except Exception as e:
        session.close()
        logger.error("connect_to_database", str(e))
        return []
    finally:
        logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
        session.close()


def get_ldap_authentication(server_name, database_name, client_id):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        session = get_database_session(connection_string[0]['transaction'])
        session_logger = get_database_session(connection_string[0]['logger'])
        logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
        records = session.query(Configurations).filter((Client.ClientId == client_id) & (Client.IsActive)).all()
        record_coll = []
        for result_elm in records:
            record_coll.append(result_elm.toDict())
        username = global_utility.get_configuration_by_key_name(record_coll, CONFIG.LDAP_USER_NAME)
        password = global_utility.get_configuration_by_key_name(record_coll, CONFIG.LDAP_USER_PASSWORD)
        server_address = global_utility.get_configuration_by_key_name(record_coll, CONFIG.LDAP_SERVER)
        server = Server(server_address, get_info=ALL, use_ssl=False)
        try:
            # Bind to the LDAP server with provided credentials
            conn = Connection(server, user=username, password=password, authentication=SIMPLE)
            if not conn.bind():
                message_info = str("LDAP a invalid set of credentials was sent to the server. Please reach out to the appropriate team member.")
                msg_array = []
                msg_array.append(message_info)
                return set_json_format(msg_array, UNAUTHORIZED_ACCESS, True, message_info), UNAUTHORIZED_ACCESS
            # If bind is successful, credentials are valid
            message_info = str("LDAP credentials were successfully validated.")
            msg_array = []
            msg_array.append(message_info)
            return set_json_format(msg_array, SUCCESS, True, message_info), SUCCESS
        except Exception as e:
            error_msg_array = []
            error_msg_array.append(str(e))
            return set_json_format(error_msg_array, INTERNAL_SERVER_ERROR, False, str(e)), INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True, logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR

def get_authentication(session, client_id, user_name):
    try:
        record = session.query(AuthTokenManagement).filter(
            (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                AuthTokenManagement.IsActive)).all()
        if len(record) > 0:
            result = global_utility.get_configuration_by_column(record)
            token = global_utility.get_list_array_value(result,
                                                        CONFIG.TOKEN)
            secret_key = global_utility.get_list_array_value(result,
                                                             CONFIG.SECRETKEY)

            decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
            auth_message = str("Authentication Token successfully validated")
            msg_array = []
            msg_array.append(auth_message)
            return set_json_format(msg_array, SUCCESS, True, auth_message), SUCCESS
        else:
            auth_message = str(f"Please register user {user_name} as they are not yet registered.")
            msg_array = []
            msg_array.append(auth_message)
            return set_json_format(msg_array, UNAUTHORIZED_ACCESS, False, auth_message), UNAUTHORIZED_ACCESS
    except jwt.ExpiredSignatureError:
        error_message = str("The token has lost its validity(expired). Kindly update the token and try it again.")
        error_msg_array = []
        error_msg_array.append(error_message)
        return set_json_format(error_msg_array, PERMISSION_ERROR, False, error_message), PERMISSION_ERROR
    except jwt.InvalidTokenError:
        error_message = str("The token that was passed is invalid. Kindly try again with the correct credentials.")
        error_msg_array = []
        error_msg_array.append(error_message)
        return set_json_format(error_msg_array, BAD_REQUEST, False, error_message), BAD_REQUEST
    except Exception as e:
        error_msg_array = []
        error_msg_array.append(str(e))
        return set_json_format(error_msg_array, INTERNAL_SERVER_ERROR, False, str(e)), INTERNAL_SERVER_ERROR


def get_token_based_authentication(server_name, database_name, client_id, user_name):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            record = session.query(AuthTokenManagement).filter(
                (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(record)}")
            if len(record) > 0:
                result = global_utility.get_configuration_by_column(record)
                token = global_utility.get_list_array_value(result,
                                                            CONFIG.TOKEN)
                secret_key = global_utility.get_list_array_value(result,CONFIG.SECRETKEY)
                decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
                error_message = str("Authentication Token successfully validated")
                msg_array = []
                msg_array.append(error_message)
                return set_json_format(msg_array, SUCCESS, True, error_message), SUCCESS
            else:
                error_message = str(f"An authentication token is not currently accessible.Please give the token to the user{user_name}.")
                msg_array = []
                msg_array.append(error_message)
                return set_json_format(msg_array, UNAUTHORIZED_ACCESS, False, error_message), UNAUTHORIZED_ACCESS
        except jwt.ExpiredSignatureError:
            error_message = str("The token has lost its validity. Kindly update the token and try it again.")
            error_msg_array = []
            error_msg_array.append(error_message)
            return set_json_format(error_msg_array, UNAUTHORIZED_ACCESS, False, error_message), UNAUTHORIZED_ACCESS
        except jwt.InvalidTokenError:
            error_message = str("The token does not working. Please pass the working token and try again.")
            error_msg_array = []
            error_msg_array.append(error_message)
            return set_json_format(error_msg_array, UNAUTHORIZED_ACCESS, False, error_message), UNAUTHORIZED_ACCESS
        except Exception as e:
            error_msg_array = []
            error_msg_array.append(str(e))
            return set_json_format(error_msg_array, INTERNAL_SERVER_ERROR, False, str(e)), INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR


def generate_authentication_token(server_name, database_name, client_id, user_name):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            record = session.query(AuthTokenManagement).filter(
                (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(record)}")
            if len(record) == 0:
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
                logger.info(f"successfully generate a token for the new user {user_name}")
                message_info = str(f"Generate Token successfully for the new user: {user_name}")
                msg_array = []
                msg_array.append(message_info)
                return set_json_format(msg_array, SUCCESS, True, message_info), SUCCESS
            else:
                logger.error("generate_authentication_token ,",f"The token cannot be generated for this user. Since this user {user_name} has already registered.")
                message_info = str(f"The token cannot be generated for this user. Since this user {user_name} has already registered.")
                msg_array = []
                msg_array.append(message_info)
                return set_json_format(msg_array, BAD_REQUEST, True, message_info), BAD_REQUEST
        except Exception as e:
            logger.error(f"In generate_authentication_token, an error happened:",str(e))
            msg_array = []
            msg_array.append(str(e))
            return set_json_format(msg_array, INTERNAL_SERVER_ERROR, False, str(e)), INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True, logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR


def update_authentication_token(server_name, database_name, client_id, user_name):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            record = session.query(AuthTokenManagement).filter(
                (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(record)}")
            if len(record) > 0:
                result = global_utility.get_configuration_by_column(record)
                record_id = global_utility.get_list_array_value(result,
                                                                CONFIG.ID)
                secret_key = secrets.token_bytes(32)
                hex_key = secret_key.hex()
                # logger.info(f"Generated secret key: {hex_key}")
                SECRET_KEY = hex_key
                # Generate a JWT token with an expiry time of 1 hour
                payload = {
                    'user_id': user_name,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                update_values = {'Token': token, 'SecretKey': SECRET_KEY, 'Modified': datetime.datetime.utcnow()}
                token_record = session.query(AuthTokenManagement).get(int(record_id))
                if token_record is not None:  # Check if the record exists
                    updated_record = session.query(AuthTokenManagement).filter_by(Id=record_id).update(update_values)
                    session.commit()
                    logger.info(f"successfully updated the user's {user_name} token.")
                    message_info = str(f"successfully updated the user's {user_name} token.")
                    msg_array = []
                    msg_array.append(message_info)
                    return set_json_format(msg_array, SUCCESS, True, message_info), SUCCESS
                else:
                    logger.info(f"{user_name}, the user, cannot locate any tokens. Please create a fresh token for the same user.")
                    message_info = str(f"{user_name}, the user, cannot locate any tokens. Please create a fresh token for the same user.")
                    msg_array = []
                    msg_array.append(message_info)
                    return set_json_format(msg_array, RESOURCE_NOT_FOUND, False, message_info), RESOURCE_NOT_FOUND
            else:
                message_info = str("There was no record to be found. Kindly get in touch with the relevant team member.")
                msg_array = []
                msg_array.append(message_info)
                return set_json_format(msg_array, RESOURCE_NOT_FOUND, False, message_info), RESOURCE_NOT_FOUND
        except Exception as e:
            logger.error(f"An update_authentication_token error occurred: ", str(e))
            msg_array = []
            msg_array.append(str(e))
            return set_json_format(msg_array, INTERNAL_SERVER_ERROR, False, str(e)), INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True, logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR


def get_connection_string(server, database, client_id):
    try:
        dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
        engine = create_engine(dns)
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(MasterTable).filter(
            (MasterTable.ClientId == client_id) & (
                MasterTable.IsActive)).all()
        record_coll = []
        for result in records:
            record_coll.append(result.toDict())
        transaction_type_connection_string = global_utility.get_connectionstring_by_connection_type(record_coll, CONFIG.CONNECTION_TYPE_TRANSACTION)
        logger_type_connection_string = global_utility.get_connectionstring_by_connection_type(record_coll, CONFIG.CONNECTION_TYPE_LOGGER)
        connection_strings= {
            'transaction':transaction_type_connection_string,
            'logger': logger_type_connection_string
        }
         # return global_utility.get_values_from_json_array(record_coll, CONFIG.CONNECTION_STRING),SUCCESS
        return [connection_strings], SUCCESS
    except Exception as e:
        error_array = []
        error_array.append(str(e))
        return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        session.close()


def get_audio_transcribe_table_data(server_name, database_name, client_id,user_name):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                status_completed = JobStatusEnum.CompletedTranscript
                status_id = status_completed.value
                results = session.query(AudioTranscribe).filter(
                    (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != int(status_id))).all()
                if len(results) > 0:
                    result_array = []
                    for result_elm in results:
                        result_array.append(result_elm.toDict())
                    return get_json_format(result_array,SUCCESS),SUCCESS
                else:
                    return get_json_format([],RESOURCE_NOT_FOUND, True, 'There is no record found in the database'),RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False,
                                   str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        return get_json_format([],INTERNAL_SERVER_ERROR,  False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def get_audio_transcribe_tracker_table_data(server_name, database_name, client_id,user_name, audio_id):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                status_completed = JobStatusEnum.CompletedTranscript
                status_id = status_completed.value
                results = session.query(AudioTranscribeTracker).filter(
                    (AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.AudioId == audio_id) & (
                            AudioTranscribeTracker.ChunkStatus != int(status_id))).all()
                if len(results) > 0:
                    result_array = []
                    for result_elm in results:
                        result_array.append(result_elm.toDict())
                    return get_json_format(result_array,SUCCESS),SUCCESS
                elif len(results) == 0:
                    return get_json_format([],RESOURCE_NOT_FOUND, True, 'There is no record found in the database'),RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False,
                                   str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        return get_json_format([], INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def get_client_master_table_configurations(server_name, database_name, client_id,user_name):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                results = session.query(ClientMaster).filter(
                    (ClientMaster.ClientId == client_id) & (ClientMaster.IsActive)).all()
                if len(results) > 0:
                    result_array = []
                    for result_elm in results:
                        result_array.append(result_elm.toDict())
                    return get_json_format(result_array,SUCCESS),SUCCESS
                elif len(results) == 0:
                    return get_json_format([],RESOURCE_NOT_FOUND, True, 'There is no record found in the database'),RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
                return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False, str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        return get_json_format([], INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def get_app_configurations(server_name, database_name, client_id,user_name):
    try:
        connection_string,status = get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                results = session.query(Client).filter((Client.ClientId == client_id) & (Client.IsActive)).all()
                if len(results) > 0:
                    result_array = []
                    for result_elm in results:
                        result_array.append(result_elm.toDict())
                    return get_json_format(result_array,SUCCESS),SUCCESS
                elif len(results) == 0:
                    return get_json_format([],RESOURCE_NOT_FOUND, True, 'There is no record found in the database'),RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        else:
            return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False, str(connection_string['message'])), RESOURCE_NOT_FOUND
    except Exception as e:
        return get_json_format([],INTERNAL_SERVER_ERROR,  False, str(e)),INTERNAL_SERVER_ERROR
    finally:
        logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
        session.close()
        session_logger.close()


def copy_audio_files_process(server_name, database_name, client_id,user_name):
    # try:
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                results_config = session.query(Configurations).filter(
                    (Configurations.ClientId == client_id) & (Configurations.IsActive)).all()
                result_config_array = []
                if len(results_config) > 0:
                    for result_elm in results_config:
                        result_config_array.append(result_elm.toDict())

                results_file_type = session.query(FileTypesInfo).filter(
                    (FileTypesInfo.ClientId == client_id) & (FileTypesInfo.IsActive)).all()
                result_file_type_array = []
                if len(results_file_type) > 0:
                    for result_elm in results_file_type:
                        result_file_type_array.append(result_elm.toDict())
                if len(result_config_array) > 0:
                    source_file_path = global_utility.get_configuration_by_key_name(result_config_array,
                                                                                    CONFIG.AUDIO_SOURCE_FOLDER_PATH)
                    destination_path = global_utility.get_configuration_by_key_name(result_config_array,
                                                                                    CONFIG.AUDIO_DESTINATION_FOLDER_PATH)
                    audio_file_size = int(
                        global_utility.get_configuration_by_key_name(result_config_array, CONFIG.AUDIO_FILE_SIZE))
                    is_validate_path = global_utility.validate_folder(source_file_path, destination_path)
                    if is_validate_path:
                        file_collection = global_utility.get_all_files(source_file_path)
                        for file in file_collection:
                            file_url = source_file_path + "/" + file
                            file_name, extension = global_utility.get_file_extension(file)
                            file_type_id = global_utility.get_file_type_by_key_name(result_file_type_array, extension)
                            if file_type_id > 0:
                                name_file = file_url.split('/')[-1].split('.')[0]
                                dir_folder_url = os.path.join(destination_path, name_file)
                                is_folder_created = global_utility.create_folder_structure(file, dir_folder_url,
                                                                                           destination_path)
                                status_processing = JobStatusEnum.Processing
                                status_id = status_processing.value
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
                                            parent_record = create_audio_file_entry(session, audio_transcribe_model)
                                            audio_chunk_process(session, client_id, parent_record, status_id,
                                                                result_file_type_array, audio_file_path,
                                                                dir_folder_url)
                                        else:
                                            audio_transcribe_model = AudioTranscribe(ClientId=client_id,
                                                                                     AudioFileName=file, JobStatus=status_id,
                                                                                     FileType=file_type_id,
                                                                                     TranscribeFilePath=audio_file_path)
                                            parent_record = create_audio_file_entry(session, audio_transcribe_model)
                                            if parent_record is not None:
                                                logger.info(f'New Item Created ID is {parent_record.Id}')
                                            chunk_transcribe_model = AudioTranscribeTracker(
                                                ClientId=client_id,
                                                AudioId=parent_record.Id,
                                                ChunkFileType=file_type_id,
                                                ChunkFileName=file, ChunkSequence=1, ChunkText='',
                                                ChunkFilePath=audio_file_path, ChunkStatus=status_id
                                            )
                                            child_record = create_audio_file_entry(session, chunk_transcribe_model)
                                            logger.info(f'Chunk New Item Created ID is {child_record.Id}')
                                    else:
                                        logger.info(f"{file} is not copied  in the destination folder {dir_folder_url}")
                                else:
                                    logger.info(f"Folder is not created for the file {file}")
                            else:
                                return get_json_format([],RESOURCE_NOT_FOUND, False, f"{file} is not supported."),RESOURCE_NOT_FOUND
                        return get_json_format([], SUCCESS,True, "All files copied and created Successfully."),SUCCESS
                    else:
                        return get_json_format([],INTERNAL_SERVER_ERROR,  False, 'There is no container at the specified path.'),INTERNAL_SERVER_ERROR
                else:
                    return get_json_format([], INTERNAL_SERVER_ERROR, False, 'There is no configuration found in the table'),INTERNAL_SERVER_ERROR
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        except Exception as e:
            return get_json_format([], INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR


def audio_chunk_process(session, client_id, parent_record, status_id, result_file_type_array, audio_file_path,
                        dir_folder_url):
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
            child_record = create_audio_file_entry(session, chunk_transcribe_model)
            logger.info(f'Chunk New Item Created ID is {child_record.Id}')


def update_audio_transcribe_tracker_status(session, record_id, status_id, update_values):
    from datetime import datetime
    record = session.query(AudioTranscribeTracker).filter_by(Id=record_id).update(update_values)
    session.commit()
    if record > 0:
        updated_record = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.Id == record_id).all()
        if len(updated_record) > 0:
            updated_result_array = []
            for result_elm in updated_record:
                updated_result_array.append(result_elm.toDict())
            logger.info(f"Id—{record_id} record in the AudioTranscribeTracker Table has been successfully updated.")
            record_data = session.query(AudioTranscribeTracker).filter(
                (AudioTranscribeTracker.ClientId == updated_result_array[0]['ClientId']) & (
                        AudioTranscribeTracker.AudioId == updated_result_array[0]['AudioId']) & (
                        AudioTranscribeTracker.ChunkStatus != status_id)).all()
            if len(record_data) == 0:
                values = {'JobStatus': status_id, "TranscribeDate": datetime.utcnow()}
                parent_record = session.query(AudioTranscribe).filter_by(Id=updated_result_array[0]['AudioId']).update(
                    values)
                session.commit()
            return set_json_format([],200, True, f"The record ID, {record_id} has been updated successfully."),SUCCESS
    else:
        return set_json_format([],500, False, f"The record ID, {record_id}, could not be found."),RESOURCE_NOT_FOUND


def retries_open_source_transcribe_audio_model(failed_file, model_name):
    retries = 2
    status = SUCCESS
    model = whisper.load_model(model_name)
    for attempt in range(retries):
        try:
            logger.info(f'fialed file process start : {failed_file}')
            time.sleep(2 ** attempt)
            result = model.transcribe(failed_file)
            return result,status
        except Exception as e:
            status = INTERNAL_SERVER_ERROR
            error_array = []
            error_array.append(str(e))
            logger.error(f"Failed to transcribe {failed_file} even after {attempt + 1} attempt(s): ",str(e))
            if retries == 2:
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR


def open_source_transcribe_audio(file_path, model_name="base"):
    try:
        status = SUCCESS
        logger.info(f"Loading from Economy Model {model_name}")
        # time.sleep(5)
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path)
        return result,status
    except Exception as e:
        logger.error('Error in Method open_source_transcribe_audio ',str(e))
        return retries_open_source_transcribe_audio_model(file_path, model_name)


def retries_open_ai_model(client, failed_file, model):
    retries = 2
    status = SUCCESS
    for attempt in range(retries):
        try:
            logger.info(f'Failed file process start : {failed_file}')
            time.sleep(2 ** attempt)
            audio_file = open(failed_file, "rb")
            transcript = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format='text',
                language='en'
            )
            return transcript,status
        except Exception as e:
            status = INTERNAL_SERVER_ERROR
            error_array = []
            error_array.append(str(e))
            logger.error(f"Failed to transcribe {failed_file} even after {attempt + 1} attempt(s): {e}",str(e))
            if retries == 2:
                return set_json_format(error_array, status, False,
                                       str(e)), status


def open_ai_transcribe_audio(transcribe_file, model="whisper-1"):
    try:
        status = SUCCESS
        logger.info(f"Loading from Premium Model {model}")
        # time.sleep(5)
        audio_file = open(transcribe_file, "rb")
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format='text',
            language='en',
            prompt= "Skit Collections Agency,Skit Collection Agency,Welcome back Mark! Thanks! We have received"
        )
        return transcript,status
    except Exception as e:
        logger.error('Error in Method open_ai_transcribe_audio ', str(e))
        error_array = []
        error_array.append(str(e))
        if isinstance(e, ConnectionError) or "429" in str(e):  # Check for connection or 429 error
            return retries_open_ai_model(client, transcribe_file, model)
        else:
            return set_json_format(error_array, RESOURCE_NOT_FOUND, False, str(e)),RESOURCE_NOT_FOUND


def update_transcribe_audio_text(server_name, database_name, client_id,user_name, file_id):
    transcript = None
    from datetime import datetime
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session,client_id,user_name)
            if auth_status == SUCCESS:
                results_config = session.query(Configurations).filter(
                    (Configurations.ClientId == client_id) & (Configurations.IsActive)).all()
                result_config_array = []
                if len(results_config) > 0:
                    for result_elm in results_config:
                        result_config_array.append(result_elm.toDict())
                if len(result_config_array) > 0:
                    whisper_model = global_utility.get_configuration_by_key_name(result_config_array, CONFIG.WHISPER_MODEL)
                    subscriptions_model = global_utility.get_configuration_by_key_name(result_config_array,
                                                                                       CONFIG.SUBSCRIPTION_TYPE)
                    processing_status = JobStatusEnum.CompletedTranscript
                    status_id= processing_status.value
                    audio_results = session.query(AudioTranscribeTracker).filter(
                        (AudioTranscribeTracker.ClientId == client_id) & (AudioTranscribeTracker.Id == file_id)).all()
                    if len(audio_results) > 0:
                        audio_result_array = []
                        for result_elm in audio_results:
                            audio_result_array.append(result_elm.toDict())
                        file_path = global_utility.get_values_from_json_array(audio_result_array, CONFIG.TRANSCRIBE_FILE_PATH)
                        check_file = os.path.isfile(file_path)
                        if not check_file:
                            error_message = 'The requested file path does not exist: '+file_path
                            logger.error('update_transcribe_audio_text:- ', error_message)
                            return set_json_format([error_message], RESOURCE_NOT_FOUND, False,
                                                   error_message), RESOURCE_NOT_FOUND
                        file_size = os.path.getsize(file_path)
                        file_size_mb = int(file_size / (1024 * 1024))
                        if file_size_mb > 15:
                            msg = 'File size greater than 10 mb so we are processing this file'
                            logger.info(msg)
                            #Need to debug this code on the server
                            # error_array = []
                            # error_array.append(msg)
                            # return set_json_format(error_array, 400, False, msg)
                    else:
                        msg = 'The file might have been deleted, renamed, moved to a different location.'
                        error_array = []
                        error_array.append(msg)
                        logger.info(msg)
                        return set_json_format(error_array, RESOURCE_NOT_FOUND, False, msg),RESOURCE_NOT_FOUND
                    start_transcribe_time = datetime.utcnow()
                    if subscriptions_model.lower() == CONSTANT.SUBSCRIPTION_TYPE_PREMIUM.lower():
                        transcript,status = open_ai_transcribe_audio(file_path)
                        if status != 200:
                            return transcript,status
                    elif subscriptions_model.lower() == CONSTANT.SUBSCRIPTION_TYPE_ECONOMY.lower():
                        transcript_whisper, status = open_source_transcribe_audio(file_path, whisper_model.lower())
                        if status == 200:
                            transcript = transcript_whisper['text']
                        else:
                            return transcript_whisper,status
                    else:
                        transcript,status = open_ai_transcribe_audio(file_path)
                        if status != 200:
                            return transcript,status

                    end_transcribe_time = datetime.utcnow()
                    update_child_values = {"ChunkText": transcript, "ChunkStatus": status_id,
                                           "ChunkTranscribeStart": start_transcribe_time,
                                           "ChunkTranscribeEnd": end_transcribe_time}
                    updated_result = update_audio_transcribe_tracker_status(session, file_id, status_id, update_child_values)
                    return updated_result
                else:
                    error_message = str(
                        f"For the passed client ID {client_id}, no configuration could be retrieved. Please try it once more with valid client ID.")
                    error_msg_array = []
                    error_msg_array.append(error_message)
                    return set_json_format(error_msg_array, RESOURCE_NOT_FOUND, False, error_message), RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}',response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False, response_message['message']), response_message['status_code']
        except Exception as e:
            error_array = []
            error_array.append(str(e).replace('[WinError 3]',''))
            logger.error('update_transcribe_audio_text:- ',str(e))
            return set_json_format(error_array,INTERNAL_SERVER_ERROR, False, str(e).replace('[WinError 3]','')),INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], RESOURCE_NOT_FOUND, False, str(connection_string['message'])), RESOURCE_NOT_FOUND

def get_file_name_pattern(server_name, database_name, client_id,user_name, file_name):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        try:
            session = get_database_session(connection_string[0]['transaction'])
            session_logger = get_database_session(connection_string[0]['logger'])
            logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
            response_message, auth_status = get_authentication(session, client_id, user_name)
            if auth_status == SUCCESS:
                results = session.query(AudioFileNamePattern).filter(
                    (AudioFileNamePattern.ClientId == client_id) & (AudioFileNamePattern.IsActive)).order_by(
                    AudioFileNamePattern.Sequence.asc()).all()
                result_array = []
                pattern_parts = []
                final_string = ''
                separator = '-'
                if len(results) > 0:
                    for result_elm in results:
                        result_array.append(result_elm.toDict())
                    separator = result_array[0]['Separator']
                    file_parts = file_name.split(separator)
                    for i in range(len(result_array)):
                        row = result_array[i];
                        if is_index_found(file_parts, i):
                            final_string += row['PatternName'] + separator
                    file_name_pattern =final_string[:-1]
                    print(file_name_pattern)
                    file_name_length = len(file_name.split(separator))
                    file_name_pattern_length = len(file_name_pattern.split(separator)) +1
                    if file_name_length >= file_name_pattern_length:
                        file_pattern_parts = file_name_pattern.split(separator)
                        key_value_pairs = []
                        # for i in range(0, len(file_pattern_parts), 2):
                        is_caseid_passed =False
                        for i in range(len(file_pattern_parts)):
                            # key, value = file_parts[i], file_parts[i + 1]
                            if file_pattern_parts[i] == 'Caseid' and separator == '-':
                                is_caseid_passed = True
                                value_file = file_parts[i] +'-'+ file_parts[i+1]
                                key, value = file_pattern_parts[i], value_file
                                key_value_pairs.append((key, value))
                            else:
                                value_file = file_parts[i]
                                if is_caseid_passed:
                                    value_file =  file_parts[i+1]
                                key, value = file_pattern_parts[i], value_file
                                key_value_pairs.append((key, value))
                        data = dict(key_value_pairs)
                        return get_json_format(data,SUCCESS,True,'Pattern matched with File Name'),SUCCESS
                    else:
                        return get_json_format([],RESOURCE_NOT_FOUND,True,'Pattern does not matched with File Name'),RESOURCE_NOT_FOUND
                elif len(results) == 0:
                    return get_json_format([],RESOURCE_NOT_FOUND, True, 'There is no record found in the database'),RESOURCE_NOT_FOUND
            else:
                logger.error(f'Token found a issue for user {user_name}', response_message['message'])
                return set_json_format([response_message['message']], response_message['status_code'], False,
                                       response_message['message']), response_message['status_code']
        except Exception as e:
            return get_json_format([],INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
    else:
        return set_json_format([connection_string['message']], INTERNAL_SERVER_ERROR, False,
                               str(connection_string['message'])), INTERNAL_SERVER_ERROR

def is_index_found(array, index):
    try:
        return array[index] is not None
    except IndexError:
        return False

def register_user(server_name, database_name, client_id,username,password):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    # get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None:
        session = global_utility.get_database_session(connection_string[0]['transaction'])
        try:
            user_creation = RegisterUser(Username=username, Password=password,ClientID=client_id)
            session.add(user_creation)
            session.commit()
            logger.info(f"username—the {username} successfully added user in RegisterUser table.")
            data ={'status':200,'message':f"{username} successfully added user in RegisterUser table"}
            return data
        except Exception as e:
            logger.error(f'Error Ocurred while adding {username}', e)

            print(e)
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR


def login_method_old(server_name, database_name, client_id,username,password):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None:
        session = global_utility.get_database_session(connection_string[0]['transaction'])
        try:
            from flask_app import bcrypt
            user = session.query(RegisterUser).filter_by(Username=username).first()
            if user and user.attempts == 0:
                if bcrypt.check_password_hash(user.Password, password):
                    user.attempts = 0  # Reset attempts if login successfull
                    check_user_exit=session.query(AuthTokenManagement).filter_by(UserName=username).first()
                    if check_user_exit:
                        token_status = get_token_based_authentication(server_name, database_name, client_id, username)
                        if token_status[0]['status'] == 'failure':
                            update_authentication_token(server_name, database_name, client_id, username)
                            data = {'status': '200','message': f'Token has been successfully updated for user {username}.'}
                            logger.info(f"Token has been successfully updated for user  {username}.")
                            return data, 200
                        else:
                            data = {'status': '401', 'message': f'Token is active for this {username}.'}
                            logger.info(f"Token is active for this  {username}.")
                            return data, 401
                    else:
                        generate_authentication_token(server_name, database_name, client_id, username)
                        # print(token_generate)
                        data = {'status': '200', 'message': f'Token created successfully for user {username}.'}
                        logger.info(f"Token created successfully for user  {username}.")
                        return data, 200
                else:
                    user.attempts += 1
                    session.commit()
                    if user.attempts >= 4:
                        user.locked = True
                        session.commit()
                        data = {'status': '401','message': f'Account locked due to too many failed attempts for {username}.'}
                        logger.info(f"Account locked due to too many failed attempts for {username}.")
                        return data, 401
                    data = {'status': '401', 'message': 'Invalid credentials.'}
                    logger.info(f"Invalid credentials.")
                    return data, 401
            else:
                data = {'status': '401', 'message': 'Invalid User or account locked.'}
                logger.info(f"Invalid User or account locked.")
                return data, 401
        except Exception as e:
            logger.error(f'Error Ocurred while adding {username}', e)
            print(e)
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR

def unlock_account(server_name, database_name, client_id,username,password):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None:
        session = global_utility.get_database_session(connection_string[0]['transaction'])
        try:
            from flask_app import bcrypt
            from datetime import datetime
            user = session.query(RegisterUser).filter_by(Username=username).first()
            if user:
                user.Password = password
                user.attempts = 0
                user.CreatedAt = datetime.utcnow()
                user.locked = False
                session.commit()
                data = {'status': '401', 'message': f'Account Successfuly unlocked with your new password'}
                logger.info(f'Account Successfuly unlocked with your new password')
                return data
            else:
                data = {'status': '401', 'message': 'Invalid User'}
                logger.info(f'Invalid User')
                return data
        except Exception as e:
            print(e)
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR

def get_exp_token_from_database(encoded_token):
    try:
        decoded_token = decode_token(encoded_token)
        # decoded_token = jwt.decode(encoded_token, algorithms=['HS256'], options={"verify_signature": False})

        exp_time = decoded_token['exp']
        data={'status':200,'message':'Token is Activated','exp_time':str(exp_time)}
        return data
    except jwt.ExpiredSignatureError:
        data={'message':'Your Token has expired.Please relogin.','status':'expire','status_code':401}
        # Handle the case where the token has expired
        return data
    except jwt.InvalidTokenError:
        data={'message':'Invalid token.','status':'expire','status_code':401}
        return data

def login_method(server_name, database_name, client_id,username,password):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None:
        session = global_utility.get_database_session(connection_string[0]['transaction'])
        try:
            from flask_app import bcrypt
            user = session.query(RegisterUser).filter_by(Username=username).first()
            if user:
                if bcrypt.check_password_hash(user.Password, password):
                    user.attempts = 0  # Reset attempts if login successful
                    session.commit()
                    #create New Token
                    import datetime
                    check_user_exit=session.query(LoginDetails).filter_by(Username=username).first()
                    if not check_user_exit:
                        import datetime
                        from flask_jwt_extended import create_access_token
                        expires_minutes = datetime.timedelta(minutes=10)
                        generate_token = create_access_token(identity=user.Id, expires_delta=expires_minutes)
                        import datetime
                        created_login_date = datetime.datetime.utcnow()
                        modified_login_date = datetime.datetime.utcnow()
                        create_login_details=LoginDetails(Username=username,ClientID=client_id,token=generate_token,Created=created_login_date,TokenModified=modified_login_date)
                        session.add(create_login_details)
                        session.commit()
                        data={'status':SUCCESS,'message':f'Token Successfully created for user {username}','token':generate_token}
                        return data
                    else:
                        get_token = session.query(LoginDetails.token).filter_by(Username=username).first()[0]
                        token_exp_time=get_exp_token_from_database(get_token)
                        if token_exp_time["status"]=="expire":
                            result=update_token(server_name, database_name, client_id, username)
                            return result
                        else:
                            data={'status':200,'message':'Token is Already activated '}
                            return data
                else:
                    user.attempts += 1
                    session.commit()
                    if user.attempts >= 4:
                        user.locked = True
                        session.commit()
                        data = {'status': '401','message': f'Account locked due to too many failed attempts for {username}.'}
                        logger.info(f"Account locked due to too many failed attempts for {username}.")
                        return data, 401
                    data = {'status': '401', 'message': 'Invalid credentials.'}
                    logger.info(f"Invalid credentials.")
                    return data, 401
            else:
                data = {'status': '401', 'message': 'Invalid User or account locked.'}
                logger.info(f"Invalid User or account locked.")
                return data, 401
        except Exception as e:
            data={'message':str(e),'status':RESOURCE_NOT_FOUND}
            logger.error(f'Error Ocurred while adding {username}', e)
            return data
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR


def update_token(server_name, database_name, client_id, username):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None:
        session = global_utility.get_database_session(connection_string[0]['transaction'])
        get_token = session.query(LoginDetails.token).filter(
            (LoginDetails.Username == username) & (LoginDetails.ClientID == client_id) & (
                Client.IsActive)).first()[0]
        user=session.query(RegisterUser).filter((RegisterUser.Username == username) & (RegisterUser.ClientID == client_id) & (
            Client.IsActive)).first()

        if user:
            import datetime
            from flask_jwt_extended import create_access_token
            expires_minutes = datetime.timedelta(minutes=10)
            generate_updated_token = create_access_token(identity=user.Id, expires_delta=expires_minutes)
            created_login_date = datetime.datetime.utcnow()
            modified_login_date = datetime.datetime.utcnow()
            update_column_dic ={"token":generate_updated_token,"Created":created_login_date, "TokenModified":modified_login_date}
            session.query(LoginDetails).filter_by(Username=username).update(update_column_dic)
            session.commit()
            data ={'message': 'Token updated successfully', 'updated_token': generate_updated_token}
            return data
        else:
            data ={'message': 'User not found'}
            return data