from app.services.logger import Logger
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from sqlalchemy import create_engine,MetaData, Table
from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker,query
from db_layer.models import Client,Configurations,Logs,BillingInformation,FileTypesInfo,Users,Subscriptions,SubscriptionPlan,AudioTranscribeTracker,AudioTranscribe
from sqlalchemy.engine import URL

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

    def get_all_configurations(self,server,database):
        try:
            # dns = f'mssql+pyodbc://{server}/{database}?driver=SQL+Server'
            dns = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()

            clients_data = session.query(Client).filter_by(ClientId=1).all()
            clients_column_names = clients_data[0].__dict__.keys() if clients_data else []
            clients_array = [{column: getattr(row, column) for column in clients_column_names} for row in clients_data]
            for i, result_array in enumerate(clients_array):
                print(f"Result set {i + 1}:")
                print(result_array)

            confguration_data = session.query(Configurations).filter_by(ClientId=1).all()
            confguration_column_names = confguration_data[0].__dict__.keys() if confguration_data else []
            confguration_array = [{column: getattr(row, column) for column in confguration_column_names} for row in confguration_data]

            filetype_info_data = session.query(FileTypesInfo).filter_by(ClientId=1).all()
            filetype_info_column_names = filetype_info_data[0].__dict__.keys() if filetype_info_data else []
            filetype_info_array = [{column: getattr(row, column) for column in filetype_info_column_names} for row in
                                  filetype_info_data]

            # users_data = session.query(Users).filter_by(ClientId=1).all()
            subscriptions_data = session.query(Subscriptions).filter_by(ClientId=1).all()
            subscriptions_column_names = subscriptions_data[0].__dict__.keys() if subscriptions_data else []
            subscriptions_array = [{column: getattr(row, column) for column in subscriptions_column_names} for row in
                                   subscriptions_data]


            subscription_plan_data = session.query(SubscriptionPlan).filter_by(ClientId=1).all()
            subscription_plan_column_names = subscription_plan_data[0].__dict__.keys() if subscription_plan_data else []
            # subscription_plan_array = [{column: getattr(row, column) for column in subscription_plan_column_names} for row in
            #                        subscription_plan_column_names]
            self.global_utility.set_client_data(clients_array)
            self.global_utility.set_configurations_data(confguration_array)
            self.global_utility.set_file_type_info_data(filetype_info_array)
            self.global_utility.set_subscription_data(subscriptions_array)
            session.close()
            configurations = {
                'Client':  clients_array,
                'Configurations': confguration_array,
                'FileTypesInfo': filetype_info_array,
                'Subscriptions': subscriptions_array,
                # 'SubscriptionPlan': subscription_plan_array
            }
            return configurations
        except Exception as e:
            session.close()
            self.logger.error("connect_to_database", e)
            raise
        finally:
            session.close()

    def save_log_table_entry_old(self,client_id,server_name,database, modul_name,level,severity, message):
        try:
            # db_server_name = self.glogal_state.get_database_server_name()
            # database_name = self.glogal_state.get_database_name()
            # client_id = self.glogal_state.get_client_id()
            dns = f'mssql+pyodbc://{server_name}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            # log_info = Logs(ClientId=client_id,LogSummary=message,LogDetails =message,LogType =level,ModulName =modul_name,Severity = severity)

            log_info = Logs(ClientId=1, LogSummary='Ldap Error', LogDetails='Ldap Error', LogType='Error',
                            ModulName='Start up process', Severity='Error')
            session.add(log_info)
            session.commit()
            session.close()
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in save_log_table_entry: {e}")
        finally:
            session.close()

    def save_log_table_entry(self,server_name,database):
        try:
            # db_server_name = self.glogal_state.get_database_server_name()
            # database_name = self.glogal_state.get_database_name()
            # client_id = self.glogal_state.get_client_id()
            dns = f'mssql+pyodbc://{server_name}/{database}?driver=ODBC+Driver+17+for+SQL+Server'
            engine = create_engine(dns)
            Session = sessionmaker(bind=engine)
            session = Session()
            # log_info = Logs(ClientId=client_id,LogSummary=message,LogDetails =message,LogType =level,ModulName =modul_name,Severity = severity)

            log_info = Logs(ClientId=1, LogSummary='Ldap Error', LogDetails='Ldap Error', LogType='Error',
                            ModulName='Start up process', Severity='Error')
            session.add(log_info)
            session.commit()
            session.close()
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in save_log_table_entry: {e}")
        finally:
            session.close()

    def create_audio_file_entry(self,model_info):
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
            session.close()
            print(f"Record inserted successfully. ID: {record_model.Id}")
            return record_model
        except Exception as e:
            session.close()
            self.logger.error(f"An error occurred in save_log_table_entry: {e}")
        finally:
            session.close()

    def update_transcribe_text(self, id, update_values, is_child_thread =True):
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
            record = session.query(model_updated).get(int(id))
            if record is not None:  # Check if the record exists
                for column, value in update_values.items():
                    setattr(record, column, value)
                # session.commit()
                print(f"Record for ID '{id}' updated successfully.")
            else:
                print(f"User with ID {id} not found.")
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
            dns  = f'mssql+pyodbc://{db_server}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
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