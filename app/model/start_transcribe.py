import os
from datetime import datetime
from app.utilities.utility import GlobalUtility
from app.utilities.db_utility import DBUtility
from app.controllers.controllers import Controller
from services.logger import Logger
from dotenv import load_dotenv
from app.db_utils import DBRecord
from app.db_connection import DbConnection
from app.service_layer.logger_utilis import LoggerUtility
from app.services.database import DataBaseClass
# from app.configs.global_state import GlobalState
from app.db_layer.models import Logs,AudioTranscribe,AudioTranscribeTracker
import re
from sqlalchemy.orm import sessionmaker
from db_layer.models import Client
from sqlalchemy import select
# from app.db_layer.models import UsersManagement
import threading

# from db_utils import DBRecord
# from db_utils import get_all_record, get_single_record, delete_single_record
# from db_utils import *
# db_instance = DBRecord()

# from app.db_layer.models import UsersManagement
# data = db_instance.get_all_record("UsersManagement")
# print("<<<<<<<<<<<< Get Start Trans>>..,",data)

load_dotenv()


class StartTranscribe:

    def __init__(self):
        self.global_utility = GlobalUtility()
        self.controller = Controller()
        self.logger = Logger()
        self.db_connection = DbConnection()
        self.db_utility = DBUtility()
        self.logger_utility = LoggerUtility()
        self.db_class = DataBaseClass()
        # self.global_state = GlobalState()
        self.db_instance = DBRecord()
    def validate_oauth_token(self, user_name):
        try:
            print("validate_oauth_token")
            client_table_data = self.db_instance.get_data_by_column_name('UsersManagement', user_name)
            self.logger.info(f'client_table_data :- {client_table_data}')
            self.logger.info(f'client_table_data :- {client_table_data}')
        except Exception as e:
            self.logger.error('validate_oauth_token', e)

    def validate_folder(self, source_file_path, destination_folder):
        try:
            # self.validate_oauth_token()
            is_source_path_exist = os.path.exists(source_file_path)
            is_destination_path_exist = os.path.exists(destination_folder)
            if is_source_path_exist and is_destination_path_exist:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error('validate_folder', e)

    def start_transcribe_process(self):
        try:
            db_server = os.getenv('DB_SERVER')
            db_name = os.getenv('DB_NAME')
            self.logger.info(f'db_server :- {db_server}')
            self.logger.info(f'db_name :- {db_name}')
            configurations = self.db_class.get_all_configurations(db_server, db_name)
            all_configurations = self.global_utility.get_config_by_key_name(configurations, 'Configurations')
            opem_key_name = self.global_utility.get_open_ai_key()
            client_id = self.global_utility.get_client_id()
            # self.db_class.get_data_from_table('Logs',client_id)
            db_server_name = self.global_utility.get_database_server_name()
            database_name = self.global_utility.get_database_name()
            source_file_path = self.global_utility.get_audio_source_folder_path()
            destination_path = self.global_utility.get_audio_destination_folder_path()
            ldap_user = self.global_utility.get_ladp_user_name()
            # ldap_pwd = None
            ldap_pwd = self.global_utility.get_ldap_user_password()
            whisper_model = self.global_utility.get_whisper_model_name()
            # self.logger.info(f'Client_ID :- {opem_key_name}','Database Server :- {db_server_name}','Database Name :- {database_name}','user name :- {ldap_user}','whisper_model :- {whisper_model}')
            success, error_message  = self.db_instance.get_ldap_authenticate(ldap_user, ldap_pwd)
            # is_authenticate = self.db_instance.get_token_based_authenticate(user_name)
            if success:
                is_validate_path = self.validate_folder(source_file_path, destination_path)
                if is_validate_path:
                    file_collection = self.global_utility.get_all_files(source_file_path)
                    self.start_recording_transcribe_process(file_collection, source_file_path, destination_path,
                                                            'Small')
                    # Premium, Normal, Small
                else:
                    self.logger.error('start_transcribe_process', 'folder path does not exist')
            else:
                log_info = Logs(ClientId=client_id, LogSummary=error_message, LogDetails=error_message,
                                LogType=self.logger.error_level_critical,
                                ModulName='start_transcribe_process', Severity=self.logger.severity_level_critical)
                self.logger.save_log_table_entry(db_server_name, database_name, log_info)
                self.logger.info('You are authenticate with the proper credentials.please try with other credentials')
        except Exception as e:
            log_info = Logs(ClientId=client_id, LogSummary=e, LogDetails=e,
                            LogType='Error',
                            ModulName='start_transcribe_process', Severity='Critical')
            self.logger.save_log_table_entry(db_server_name, database_name, log_info)
            self.logger.error('start_transcribe_process', e)
            # self.db_class.save_log_table_entry('start_transcribe_process','ERROR','ERROR',e)

    def start_recording_transcribe_process(self, file_collection, source_file_path, destination_path,
                                           subscription_model):
        try:
            transcribe_files = []
            for file in file_collection:
                file_url = source_file_path + "/" + file
                file_name, extension = self.global_utility.get_file_extension(file)
                if extension == ".wav" or extension == ".mp3":
                    name_file = file_url.split('/')[-1].split('.')[0]
                    dir_folder_url = os.path.join(destination_path, name_file)
                    print('Audio File name for folder creation : ', name_file)
                    # model details, subscription
                    is_folder_created = self.global_utility.create_folder_structure(file, dir_folder_url,
                                                                                    destination_path)
                    if is_folder_created:
                        is_copied_files = self.global_utility.copy_file(file_url, dir_folder_url)
                        if is_copied_files:
                            audio_file_path = os.path.join(dir_folder_url, file)
                            file_size = os.path.getsize(audio_file_path)
                            file_size_mb = file_size / (1024 * 1024)
                            audio_file_size = self.global_utility.get_audio_max_file_size()

                            if file_size_mb > audio_file_size:
                                self.logger.info(f'file size :- {file_size}')
                                audio_transcibe_model = AudioTranscribe(ClientId=self.global_utility.get_client_id(),
                                                                        AudioFileName=file, JobStatus='Starting',
                                                                        FileType=extension, TranscribeText='',
                                                                        TranscribeFilePath=audio_file_path)
                                parent_record = self.db_class.create_audio_file_entry(audio_transcibe_model)
                                self.start_process_recordings_large_file(parent_record,audio_file_path, dir_folder_url, name_file,
                                                                         subscription_model, transcribe_files)
                            else:
                                audio_transcibe_model = AudioTranscribe(ClientId=self.global_utility.get_client_id(),
                                                                        AudioFileName=file, JobStatus='Starting',
                                                                        FileType=extension, TranscribeText='',
                                                                        TranscribeFilePath=audio_file_path)
                                parent_record = self.db_class.create_audio_file_entry(audio_transcibe_model)
                                chunk_transcibe_model = AudioTranscribeTracker(
                                    ClientId=self.global_utility.get_client_id(),
                                    AudioId=parent_record.Id,
                                    AudioFileName=file, ChunkSequence=1, ChunkText='',
                                    ChunkFilePath=audio_file_path, ChunkStatus='Drafted',
                                    ChunkCreatedDate=datetime.utcnow())
                                parent_record = self.db_class.create_audio_file_entry(chunk_transcibe_model)
                                self.start_process_recordings(parent_record,parent_record,audio_file_path, dir_folder_url, name_file,
                                                              subscription_model, transcribe_files)
                        else:
                            self.logger.error('start_recording_transcribe_process',
                                              f"{file} is not copied  in the destination folder {dir_folder_url}")
                    else:
                        self.logger.error('start_recording_transcribe_process',
                                          f"Folder is not created for the file {file}")
                else:
                    self.logger.error('start_recording_transcribe_process', f"{file} is not supported.")
            self.logger.info(f"All Transcribe files: {transcribe_files}")
        except Exception as e:
            self.logger.error('start_recording_transcribe_process', f'Error while creating build_transcribe_model {e}')

    def start_process_recordings_large_file(self,parent_record, audio_file_path, dir_folder_url, name_file, subscription_model,
                                            transcribe_files):
        try:
            chunks = self.global_utility.split_audio_chunk_files(audio_file_path, dir_folder_url)
            chunks_files = chunks[0]
            # chunk_chunk_files_path = chunks[1]
            txt_file = os.path.join(dir_folder_url, name_file) + '.txt'
            transcribe_files.append(txt_file)

            for i in range(len(chunks_files)):
                chunk_file = f"{dir_folder_url}/chunk_{i}.wav"
                file_name, extension = self.global_utility.get_file_extension(f"chunk_{i}.wav")
                chunk_transcibe_model = AudioTranscribeTracker(ClientId=self.global_utility.get_client_id(),
                                                        AudioId=parent_record.Id,
                                                        AudioFileName=f"chunk_{i}.wav", ChunkSequence=i, ChunkText='',
                                                        ChunkFilePath=chunk_file,ChunkStatus ='Drafted',
                                                               ChunkCreatedDate = datetime.utcnow())
                child_record = self.db_class.create_audio_file_entry(chunk_transcibe_model)
            for i in range(len(chunks_files)):
                chunk_file = f"{dir_folder_url}/chunk_{i}.wav"
                self.logger.info(f'Open Ai Chunk Audio File Path:- {chunk_file}')
                transcript = self.controller.build_transcribe_audio(chunk_file, subscription_model)
                # threading.Thread(target= transcript, args=(chunk_file,)).start()
                is_text_file_written = self.global_utility.wrire_txt_file(txt_file, transcript)
        except Exception as e:
            self.logger.error('start_process_recordings_large_file', e)

    def start_process_recordings(self, parent_record,child_record,audio_file_path, dir_folder_url, name_file, subscription_model,
                                 transcribe_files):
        try:
            start_transcribe_time = datetime.utcnow()
            txt_file = os.path.join(dir_folder_url, name_file) + '.txt'
            transcript = self.controller.build_transcribe_audio(audio_file_path, subscription_model)
            end_transcribe_time = datetime.utcnow()
            update_values = {"TranscribeText": transcript['text'],"JobStatus":"Completed",
                                   "TranscribeStartTime": start_transcribe_time,
                                   "TranscribeEndTime": end_transcribe_time,'TranscribeDate':end_transcribe_time}
            update_child_values = {"ChunkText": transcript['text'], "ChunkStatus": "Completed",
                             "ChunkTranscribeStart": start_transcribe_time, "ChunkTranscribeEnd": end_transcribe_time}
            self.db_class.update_transcribe_text(parent_record.Id, update_values,False)
            self.db_class.update_transcribe_text(child_record.Id, update_child_values)
            transcribe_files.append(txt_file)
            is_text_file_written = self.global_utility.wrire_txt_file(txt_file, transcript)
        except Exception as e:
            self.logger.error('start_process_recordings', e)

    # def process_recordings(self,audio_file_path,dir_folder_url,name_file):
    #     chunks = self.global_utility.split_audio_chunk_files(audio_file_path,dir_folder_url)
    #     chunks_files = chunks[0]
    #     chunk_chunk_files_path = chunks[1]
    #     txt_file = os.path.join(dir_folder_url, name_file)+'.txt'
    #     for i in range(len(chunks_files)):
    #         chunk_file = f"{dir_folder_url}/chunk_{i}.wav"
    #         print(' Open Ai Chunk Audio File Path',chunk_file)
    #         # transcript = self.controller.build_chunk_files_transcribe_audio(self,chunks[0],chunks[1],subscription_model)
    #         transcript = self.controller.build_transcribe_audio(chunk_file,subscription_model)
    #         threading.Thread(target= transcript, args=(chunk_file,)).start()
    #         is_text_file_written = self.global_utility.wrire_txt_file(txt_file,transcript)
