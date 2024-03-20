from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from sqlalchemy import create_engine, MetaData, Table
from app.configs.config import CONFIG
from sqlalchemy.orm import sessionmaker
import jwt
import datetime
import secrets
from ldap3 import Server, Connection, ALL, SIMPLE
from db_layer.models import (Client, Configurations, Logs, FileTypesInfo, Subscriptions, AudioTranscribeTracker, \
    AudioTranscribe, ClientMaster, AuthTokenManagement,JobStatus,SubscriptionPlan,MasterConnectionString, \
                             MasterConnectionString)

dns = f'mssql+pyodbc://FLM-VM-COGAIDEV/AudioTrans?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(dns)
Session = sessionmaker(bind=engine)
session = Session()
conn = engine.raw_connection()
cursor = conn.cursor()


class FlaskDBService:
    _instance = None
    global_utility = GlobalUtility()
    logger = Logger()
    db_connection = DbConnection()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def get_json_format(self,result, status=True, message=None):
        api_object = {
            "result": result,
            "message": message == None if 'The data result set that the service provided.' else message,
            "status": 'success',
        }
        if status == False:
            api_object = {
                "result": [],
                "message": message,
                "status": 'failure',
            }
        return api_object

    def set_json_format(self,result, status=True, message=None):
        api_object = {
            "result": result,
            "message": message == None if 'Record has been updated successfully.' else message,
            "status": 'success',
        }
        if status == False:
            api_object = {
                "result": [],
                "message": message,
                "status": 'failure',
            }
        return api_object

    def is_empty(value):
        return value is None or (isinstance(value, str) and not value.strip())

    def get_all_configurations(self, server, database, client_id):
        try:
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
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

            self.global_utility.set_client_data(client_coll)
            self.global_utility.set_configurations_data(configuration_coll)
            self.global_utility.set_file_type_info_data(filetype_info_coll)
            self.global_utility.set_subscription_data(subscriptions_array)
            self.global_utility.set_job_status_data(job_status_coll)
            self.global_utility.set_subscription_plan_data(subscriptions_plan_coll)
            configurations = {
                'Client': client_coll,
                'Configurations': configuration_coll,
                'FileTypesInfo': filetype_info_coll,
                'Subscriptions': subscriptions_array,
                'JobStatus': job_status_coll
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
            audio_transcribe = session.query(AudioTranscribe).filter(
                (AudioTranscribe.ClientId == client_id) & (AudioTranscribe.JobStatus != 'Completed')).all()
            audio_transcribe_array = []
            for contact in audio_transcribe:
                audio_transcribe_array.append(contact.toDict())
            return audio_transcribe_array
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
                return self.set_json_format([record_id])
            else:
                return self.set_json_format([], False, f"The record ID, {record_id}, could not be found.")

        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
            return self.set_json_format([], False, e)
        finally:
            session.close()

    def update_audio_transcribe_tracker_table(self, server_name, database_name, record_id, update_values):
        try:
            dns = f'mssql+pyodbc://{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(AudioTranscribeTracker).get(int(record_id))
            if len(record) > 0:  # Check if the record exists
                for column, value in update_values.items():
                    setattr(record, column, value)
                session.commit()
                self.logger.info(f"Child Record for ID '{record_id}' updated successfully.")
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
                return self.set_json_format([record_id])
            else:
                return self.set_json_format([], False, f"The record ID, {record_id}, could not be found.")
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
            return self.set_json_format([], False, e)
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
                self.generate_token(session, client_id, user_name)
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            self.update_token(session, record_id, user_name)
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

    def generate_token(self, session, client_id, user_name):
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
            self.logger.info(f"Record inserted successfully. ID: {record_model.Id}")
            return record_model
            print("Generated token:", record_model.Id)
        except Exception as e:
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            session.close()

    def update_token(self, session, record_id, user_name):
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
            self.logger.info(f"Record inserted successfully. ID: {record.Id}")
            # return record
            print("Generated token:", record.Id)
        except Exception as e:
            self.logger.error(f"An error occurred in update_transcribe_text: {e}")
        finally:
            session.close()

    def get_connection_string(self, server, database, client_id):
        try:
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            records = session.query(MasterConnectionString).filter(
                (MasterConnectionString.ClientId == client_id) &  (
                    MasterConnectionString.IsActive)).all()
            record_coll = []
            for result in records:
                record_coll.append(result.toDict())
            return self.global_utility.get_values_from_json_array(record_coll, CONFIG.CONNECTION_STRING)
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            return []
        finally:
            session.close()
