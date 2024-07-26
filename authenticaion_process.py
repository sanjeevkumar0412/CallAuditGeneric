from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
global_utility = GlobalUtility()
logger = Logger()
db_connection = DbConnection()
import jwt
from app.configs.error_code_enum import *
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, get_jwt, decode_token

from db_layer.models import (Client,AuthTokenManagement,RegisterUser,LoginDetails)
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
            client_systems ={}
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
                        import datetime,hashlib
                        from flask import request
                        from flask_jwt_extended import create_access_token
                        access_token = create_access_token(identity=user.Id, expires_delta=False)
                        expires_minutes = datetime.timedelta(minutes=10)
                        refresh_token = create_access_token(identity=user.Id, expires_delta=expires_minutes)
                        client_identifier = hashlib.sha256(request.remote_addr.encode()).hexdigest()
                        client_systems[refresh_token] = client_identifier
                        created_login_date = datetime.datetime.utcnow()
                        modified_login_date = datetime.datetime.utcnow()
                        create_login_details=LoginDetails(Username=username,ClientID=client_id,token=access_token,Created=created_login_date,TokenModified=modified_login_date,refresh_token=refresh_token,clientIdentifier=client_identifier)
                        session.add(create_login_details)
                        session.commit()
                        data={'status':SUCCESS,'message':f'Token Successfully created for user {username}','access_token':access_token}
                        return data
                    else:
                        get_token = session.query(LoginDetails.refresh_token).filter_by(Username=username).first()[0]
                        token_exp_time=get_exp_token_from_database(get_token)
                        if token_exp_time["status"]=="expire":
                            result=update_token(server_name, database_name, client_id, username)
                            return result
                        else:
                            update_token(server_name, database_name, client_id, username)
                            data={'status':200,'message':'Token has been refreshed '}
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
        access_token = session.query(LoginDetails.token).filter(
            (LoginDetails.Username == username) & (LoginDetails.ClientID == client_id) & (
                Client.IsActive)).first()[0]
        user=session.query(RegisterUser).filter((RegisterUser.Username == username) & (RegisterUser.ClientID == client_id) & (
            Client.IsActive)).first()
        if user:
            import datetime
            from flask_jwt_extended import create_access_token
            expires_minutes = datetime.timedelta(minutes=10)
            refresh_token_updated = create_access_token(identity=user.Id, expires_delta=expires_minutes)
            created_login_date = datetime.datetime.utcnow()
            modified_login_date = datetime.datetime.utcnow()
            update_column_dic ={"refresh_token":refresh_token_updated,"Created":created_login_date, "TokenModified":modified_login_date}
            session.query(LoginDetails).filter_by(Username=username).update(update_column_dic)
            session.commit()
            data ={'message': 'Token updated successfully', 'access_token':access_token,'status': SUCCESS}
            return data
        else:
            data ={'message': 'User not found'}
            return data