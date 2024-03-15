from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from sqlalchemy import create_engine, MetaData, Table
from app.configs.config import CONFIG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import jwt
import datetime
import secrets
from ldap3 import Server, Connection, ALL, SIMPLE
from db_layer.models import Client, Configurations, Logs, FileTypesInfo, Subscriptions, AudioTranscribeTracker, \
    AudioTranscribe, ClientMaster, AuthTokenManagement


class DataBaseClass:
    _instance = None

    def __init__(self):
        self.global_utility = GlobalUtility()
        self.logger = Logger()
        self.db_connection = DbConnection()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_all_configurations(self, server, database, client_id):
        try:
            # dns = f'mssql+pyodbc://{server}/{database}?driver=SQL+Server'
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            # Get data from Client table
            clients_data = session.query(Client).filter_by(ClientId=client_id).all()
            clients_array = self.global_utility.get_configuration_by_column(clients_data)
            # Get data from Configuration table
            configuration_data = session.query(Configurations).filter_by(ClientId=client_id).all()
            configuration_array = self.global_utility.get_configuration_by_column(configuration_data)
            # Get data from FileTypeInfo table
            filetype_info_data = session.query(FileTypesInfo).filter_by(ClientId=client_id).all()
            filetype_info_array = self.global_utility.get_configuration_by_column(filetype_info_data)
            # Get data from Subscription table
            subscriptions_data = session.query(Subscriptions).filter_by(ClientId=client_id).all()
            subscriptions_array = self.global_utility.get_configuration_by_column(subscriptions_data)
            # Set the configuration data in utility variables
            self.global_utility.set_client_data(clients_array)
            self.global_utility.set_configurations_data(configuration_array)
            self.global_utility.set_file_type_info_data(filetype_info_array)
            self.global_utility.set_subscription_data(subscriptions_array)
            configurations = {
                'Client': clients_array,
                'Configurations': configuration_array,
                'FileTypesInfo': filetype_info_array,
                'Subscriptions': subscriptions_array
            }
            return configurations
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            raise
        finally:
            session.close()

    def save_log_table_entry(self, server_name, database):
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
            self.logger.error(f"An error occurred in save_log_table_entry: {e}")
        finally:
            session.close()

    def create_audio_file_entry(self, model_info):
        try:
            db_server = self.global_utility.get_database_server_name()
            db_name = self.global_utility.get_database_name()
            dns = f'mssql+pyodbc://{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            record_model = model_info
            session.add(record_model)
            session.commit()
            self.logger.info(f"Record inserted successfully. ID: {record_model.Id}")
            return record_model
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in save_log_table_entry: ", {e})
        finally:
            session.close()

    def update_transcribe_text(self, record_id, update_values, is_child_thread=True):
        try:
            db_server = self.global_utility.get_database_server_name()
            db_name = self.global_utility.get_database_name()
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
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            session.close()

    def get_data_from_table(self, table_name, client_id):
        try:
            db_server = self.global_utility.get_database_server_name()
            db_name = self.global_utility.get_database_name()
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
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            result.close()

    def get_audio_transcribe_table_data(self, server, database, client_id):
        try:
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            records = session.query(AudioTranscribe).filter(
                (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != 'Completed')).all()
            return records
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            raise
        finally:
            session.close()

    def get_audio_transcribe_tracker_table_data(self, server, database, client_id, audio_parent_id):
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
            self.logger.error("connect_to_database", e)
        finally:
            session.close()

    def update_audio_transcribe_table(self, server_name, database_name, record_id, update_values):
        try:
            dns = f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(AudioTranscribe).get(int(record_id))
            if record is not None:  # Check if the record exists
                for column, value in update_values.items():
                    setattr(record, column, value)
                session.commit()
                print(f"Parent Record for ID '{record_id}' updated successfully.")
            else:
                print(f"User with ID {record_id} not found.")
            return {
                'status': 'Success',
                'message': f"Record for ID '{record_id}' updated successfully.",
                'code': 200
            }
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
            return {
                'status': 'Failure',
                'message': e,
                'code': 400
            }
        finally:
            session.close()

    def update_audio_transcribe_tracker_table(self, server_name, database_name, record_id, update_values):
        try:
            dns = f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(AudioTranscribeTracker).get(int(record_id))
            if record is not None:  # Check if the record exists
                for column, value in update_values.items():
                    setattr(record, column, value)
                session.commit()
                self.logger.info(f"Child Record for ID '{record_id}' updated successfully.")
            else:
                self.logger.info(f"User with ID {record_id} not found.")
            # session.commit()
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
                    self.logger.info(f"Record for ID '{parent_record}' updated successfully.")
            session.close()
            return {
                'status': 'Success',
                'message': f"Record for ID '{record_id}' updated successfully.",
                'code': 200
            }
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
            return {
                'status': 'Failure',
                'message': e,
                'code': 400
            }
        finally:
            session.close()

    def get_client_configurations(self, server, database, client_id, master_client_user):
        try:
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            records = session.query(Client).filter(
                (Client.ClientId == client_id) & (Client.ClientUserName == master_client_user) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(records)}")
            client_result = self.global_utility.get_configuration_by_column(records)
            self.global_utility.set_client_data(client_result)
            return client_result
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            return []
        finally:
            session.close()

    def get_oauth_access_token(self, server, database, user_name, secret_key):
        try:
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            records = session.query(Client).filter(
                (Client.ClientUserName == user_name) & (Client.ClientPassword == secret_key) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(records)}")
            client_result = self.global_utility.get_configuration_by_column(records)
            self.global_utility.set_client_data(client_result)
            return client_result
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            return []
        finally:
            session.close()

    def get_client_master_data(self, server, database, client_id):
        try:
            connection_string1 = "DRIVER={SQL Server Native Client 10.0};SERVER=FLM-VM-COGAIDEV;DATABASE=AudioTrans;UID=user;PWD=password"
            connection_string = "DRIVER={ODBC+Driver+17+for+SQL+Server};SERVER=FLM-VM-COGAIDEV;DATABASE=AudioTrans;UID=agreeya\sudhir.kumar;PWD=Solenki1@#"
            connection_string2 = "DRIVER={ODBC+Driver+17+for+SQL+Server};SERVER=FLM-VM-COGAIDEV;DATABASE=AudioTrans"
            connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})

            # engine = create_engine(connection_url)
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            records = session.query(ClientMaster).filter(Client.ClientId == client_id).all()
            client_result = self.global_utility.get_configuration_by_column(records)
            self.global_utility.set_master_client_data(client_result)
            return client_result
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            return []
        finally:
            session.close()

    def get_ldap_authenticate(self, username, password):
        success = True
        error_message = None
        # Establish connection with the LDAP server
        # server_address = 'LDAP://agreeya.local/DC=agreeya,DC=local'
        server_address = 'ldap://10.9.32.17:389'
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

    def get_token_based_authenticate(self, server, database, client_id, user_name):

        try:
            success = True
            error_message = None
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(AuthTokenManagement).filter(
                (AuthTokenManagement.UserName == user_name) & (AuthTokenManagement.ClientId == client_id) & (
                    Client.IsActive)).all()
            print(f"Records Length :- {len(record)}")
            if len(record) > 0:
                result = self.global_utility.get_configuration_by_column(record)
                token = self.global_utility.get_list_array_value(result,
                                                                 CONFIG.TOKEN)
                record_id = self.global_utility.get_list_array_value(result,
                                                                 CONFIG.ID)
                secret_key = self.global_utility.get_list_array_value(result,
                                                                      CONFIG.SECRETKEY)

                decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
                print("Decoded token:", decoded_token)
                success = True
                error_message = str("Token verified successfully")
                return success, error_message
            else:
                self.generate_token(session,client_id, user_name)
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            self.update_token(session, record_id,user_name)
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

    def generate_token(self, session,client_id, user_name):
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
            record_model = AuthTokenManagement(Token=token, UserName=user_name, ClientId=client_id, SecretKey=SECRET_KEY)
            session.add(record_model)
            session.commit()
            self.logger.info(f"Record inserted successfully. ID: {record_model.Id}")
            return record_model
            print("Generated token:", record_model.Id)
        except Exception as e:
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            session.close()


    def update_token(self, session,record_id, user_name):
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
            update_values = {'Token': token,'SecretKey': SECRET_KEY}
            record = session.query(AudioTranscribeTracker).get(int(record_id))
            if record is not None:  # Check if the record exists
                for column, value in update_values.items():
                    setattr(record, column, value)
                session.commit()
            self.logger.info(f"Record inserted successfully. ID: {record.Id}")
            # return record
            print("Generated token:", record.Id)
        except Exception as e:
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            session.close()
