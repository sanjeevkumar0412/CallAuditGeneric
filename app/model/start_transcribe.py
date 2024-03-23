import os
from datetime import datetime
from app.configs.config import CONFIG
from app.utilities.utility import GlobalUtility
from services.logger import Logger
from dotenv import load_dotenv
from app.db_utils import DBRecord
from app.db_connection import DbConnection
from app.services.database import DataBaseClass
from app.db_layer.models import Logs, AudioTranscribe, AudioTranscribeTracker
from constants.constant import CONSTANT

load_dotenv()


class StartTranscribe:

    def __init__(self):
        self.global_utility = GlobalUtility()
        self.logger = Logger()
        self.db_connection = DbConnection()
        self.database_class = DataBaseClass()
        self.db_instance = DBRecord()

    def validate_folder(self, source_file_path, destination_folder):
        try:
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
            db_server_name = os.getenv('DB_SERVER')
            db_sql_name = os.getenv('DB_NAME')
            user_name = os.getenv('OAUTH_USER_NAME')
            client = int(os.getenv('CLIENT_ID'))
            self.logger.info(f'db_server :- {db_server_name}')
            self.logger.info(f'db_name :- {db_sql_name}')
            # get the master table data
            master_configurations = self.database_class.get_client_master_data(db_server_name, db_sql_name, client)
            # all master table configurations
            master_client_id = int(self.global_utility.get_values_from_json_array(master_configurations, CONFIG.CLIENT_ID))
            master_db_server = self.global_utility.get_values_from_json_array(master_configurations, CONFIG.SERVER_NAME)
            master_db_name = self.global_utility.get_values_from_json_array(master_configurations, CONFIG.DATABASE_NAME)
            master_client_user = self.global_utility.get_values_from_json_array(master_configurations, CONFIG.CLIENT_USER)
            # authentication the configure user
            client_config_result = self.database_class.get_client_configurations(master_db_server, master_db_name,
                                                                                 master_client_id, master_client_user)
            if len(client_config_result) > 0:
                authentication_type = self.global_utility.get_values_from_json_array(client_config_result,
                                                                               CONFIG.AUTHENTICATION_TYPE)
                client_user_name = self.global_utility.get_values_from_json_array(client_config_result,
                                                                            CONFIG.CLIENT_USER_NAME)
                client_user_password = self.global_utility.get_values_from_json_array(client_config_result,
                                                                                CONFIG.CLIENT_PASSWORD)
                client_id = int(self.global_utility.get_values_from_json_array(client_config_result, CONFIG.CLIENT_ID))
                db_server = self.global_utility.get_values_from_json_array(client_config_result, CONFIG.SERVER_NAME)
                db_name = self.global_utility.get_values_from_json_array(client_config_result, CONFIG.DATABASE_NAME)
                # oauth authentication_type
                if authentication_type == CONSTANT.AUTHENTICATION_OAUTH:
                    success, error_message = self.database_class.get_token_based_authenticate(db_server, db_name,
                                                                                              client_id, user_name)
                else:
                    # ldap authentication_type
                    success, error_message = self.database_class.get_ldap_authenticate(client_user_name,
                                                                                       client_user_password)
                # authentication process completed
                if success:
                    configurations = self.database_class.get_all_configurations(db_server, db_name,
                                                                                master_client_id)
                    self.logger.info('All Configuration getting successfully!')
                    opem_key_name = 'sk-' + self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.OPENAI_API_KEY)

                    name_client = int(self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.CLIENT_ID))
                    db_server_name = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.DATABASE_SERVER)
                    database_name =  self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.DATABASE_SERVER)

                    self.logger.info('self.database_class.get_audio_transcribe_tracker_table_data')
                    source_file_path = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.AUDIO_SOURCE_FOLDER_PATH)
                    destination_path = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.AUDIO_DESTINATION_FOLDER_PATH)
                    ldap_user = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.LDAP_USER_NAME)
                    # ldap_pwd = None
                    ldap_pwd = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.LDAP_USER_PASSWORD)
                    whisper_model = self.global_utility.get_configuration_by_key_name(self.global_utility.cofigurations_data,CONFIG.WHISPER_MODEL)
                    is_validate_path = self.validate_folder(source_file_path, destination_path)
                    if is_validate_path:
                        file_collection = self.global_utility.get_all_files(source_file_path)
                        self.start_recording_transcribe_process(client_id,file_collection, source_file_path, destination_path,
                                                                whisper_model)
                        # Premium, Normal, Small
                    else:
                        self.logger.info('There is no container at the specified path.')
            else:
                self.logger.info(
                    'You are not authenticate with the proper credentials.please try with other credentials')
        except Exception as e:
            log_info = Logs(ClientId=client_id, LogSummary=e, LogDetails=e,
                            LogType='Error',
                            ModulName='start_transcribe_process', Severity='Critical')
            self.logger.save_log_table_entry(db_server_name, database_name, log_info)
            self.logger.error('start_transcribe_process', e)

    def start_recording_transcribe_process(self, client_id,file_collection, source_file_path, destination_path,
                                           subscription_model):
        try:
            transcribe_files = []
            for file in file_collection:
                file_url = source_file_path + "/" + file
                file_name, extension = self.global_utility.get_file_extension(file)
                file_type_id = self.global_utility.get_file_type_by_key_name(
                    self.global_utility.get_file_type_info_data(), extension)
                if extension == ".wav" or extension == ".mp3":
                    name_file = file_url.split('/')[-1].split('.')[0]
                    dir_folder_url = os.path.join(destination_path, name_file)
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
                                self.logger.info(f'file {name_file} Starting with size :- {file_size}')
                                status_id = self.global_utility.get_status_by_key_name(
                                    self.global_utility.get_job_status_data(), 'PreProcessing')
                                audio_transcribe_model = AudioTranscribe(ClientId=client_id,
                                                                        AudioFileName=file, JobStatus=status_id,
                                                                        FileType=file_type_id,
                                                                        TranscribeFilePath=audio_file_path)
                                parent_record = self.database_class.create_audio_file_entry(audio_transcribe_model)
                                self.start_process_recordings_large_file(client_id,parent_record, audio_file_path, dir_folder_url,
                                                                         name_file,
                                                                         subscription_model, transcribe_files)
                            else:
                                self.logger.info(f'file {name_file} Starting with size :- {file_size}')
                                self.logger.info(f'file {name_file} Starting with size :- {file_size}')
                                status_id = self.global_utility.get_status_by_key_name(
                                    self.global_utility.get_job_status_data(), 'PreProcessing')
                                audio_transcribe_model = AudioTranscribe(ClientId=client_id,
                                                                        AudioFileName=file, JobStatus=status_id,
                                                                        FileType=file_type_id,
                                                                        TranscribeFilePath=audio_file_path)
                                parent_record = self.database_class.create_audio_file_entry(audio_transcribe_model)
                                if parent_record is not None:
                                    self.logger.info(f'New Item Created ID is {parent_record.Id}')
                                chunk_transcribe_model = AudioTranscribeTracker(
                                    ClientId=client_id,
                                    AudioId=parent_record.Id,
                                    ChunkFileType=file_type_id,
                                    ChunkFileName=file, ChunkSequence=1, ChunkText='',
                                    ChunkFilePath=audio_file_path, ChunkStatus=status_id,
                                    ChunkCreatedDate=datetime.utcnow())
                                parent_record = self.database_class.create_audio_file_entry(chunk_transcribe_model)
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

    def start_process_recordings_large_file(self, client_id,parent_record, audio_file_path, dir_folder_url, name_file,
                                            subscription_model,
                                            transcribe_files):
        try:
            chunks = self.global_utility.split_audio_chunk_files(audio_file_path, dir_folder_url)
            chunks_files = chunks[0]
            # chunk_chunk_files_path = chunks[1]
            txt_file = os.path.join(dir_folder_url, name_file) + '.txt'
            transcribe_files.append(txt_file)
            db_server_name = 'FLM-VM-COGAIDEV'
            database_name = 'AudioTrans'
            # db_server_name = self.global_utility.get_database_server_name()
            # database_name = self.global_utility.get_database_name()
            status_id = self.global_utility.get_status_by_key_name(self.global_utility.get_job_status_data(),
                                                                   'PreProcessing')
            counter = 0
            for filename in os.listdir(dir_folder_url):
                if filename.endswith(".wav"):  # Replace ".wav" with your audio format
                    counter += 1
                    filepath = os.path.join(dir_folder_url, filename)
                    file_name, extension = self.global_utility.get_file_extension(filename)
                    file_type_id = self.global_utility.get_file_type_by_key_name(
                        self.global_utility.get_file_type_info_data(), extension)
                    chunk_transcribe_model = AudioTranscribeTracker(ClientId=client_id,
                                                                    AudioId=parent_record.Id,
                                                                    ChunkFileName=filename, ChunkSequence=counter,
                                                                    ChunkText='',
                                                                    ChunkFileType=file_type_id,
                                                                    ChunkFilePath=filepath, ChunkStatus=status_id,
                                                                    ChunkCreatedDate=datetime.utcnow())
                    child_record = self.database_class.create_audio_file_entry(chunk_transcribe_model)
                    self.start_process_recordings(self, child_record, audio_file_path,subscription_model)
                    self.logger.info(
                        f"Sql Table Entry Completed file chunk_{filename}.wav inside folder {dir_folder_url}")
        except Exception as e:
            self.logger.error('start_process_recordings_large_file', e)

    def start_process_recordings(self, child_record, audio_file_path, subscription_model):
        try:
            start_transcribe_time = datetime.utcnow()
            transcript = self.controller.build_transcribe_audio(audio_file_path, subscription_model)
            end_transcribe_time = datetime.utcnow()
            update_child_values = {"ChunkText": transcript['text'], "ChunkStatus": 1,
                                   "ChunkTranscribeStart": start_transcribe_time,
                                   "ChunkTranscribeEnd": end_transcribe_time}
            db_server_name = 'FLM-VM-COGAIDEV'
            database_name = 'AudioTrans'
            self.database_class.update_audio_transcribe_tracker_table(db_server_name, database_name, child_record.Id,
                                                                      update_child_values)
        except Exception as e:
            self.logger.error('start_process_recordings', e)
