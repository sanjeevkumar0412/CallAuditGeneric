from pydub import AudioSegment
from dotenv import load_dotenv
import shutil
import os
import jwt
import secrets
from datetime import datetime
from app.configs.config import CONFIG
from app.services.logger import Logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


class GlobalUtility:
    _instance = None

    # place keys here

    def __init__(self):
        self.logger = Logger()
        self.cofigurations_data = None
        self.user_management_data = None
        self.client_data = None
        self.subscription_plan_data = None
        self.subscription_data = None
        self.billing_information_data = None
        self.job_status_data = None
        self.file_type_info_data = None
        # self.global_state = GlobalState()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def get_key_config_value(self, key_name):
        return self.get_config_by_value(self.cofigurations_data, key_name)

    def set_configurations_data(self, data):
        self.cofigurations_data = data

    def get_cofigurations_data(self):
        return self.cofigurations_data

    def set_user_management_data(self, data):
        self.user_management_data = data

    def get_user_management_data(self):
        return self.user_management_data

    def set_client_data(self, data):
        self.client_data = data

    def get_client_data(self):
        return self.client_data

    def set_subscription_plan_data(self, data):
        self.subscription_plan_data = data

    def get_subscription_plan_data(self):
        return self.subscription_plan_data

    def set_subscription_data(self, data):
        self.subscription_data = data

    def get_subscription_data(self):
        return self.subscription_data

    def set_billing_information_data(self, data):
        self.billing_information_data = data

    def get_billing_information_data(self):
        return self.billing_information_data

    def set_job_status_data(self, data):
        self.job_status_data = data

    def get_job_status_data(self):
        return self.job_status_data

    def set_file_type_info_data(self, data):
        self.file_type_info_data = data

    def get_file_type_info_data(self):
        return self.file_type_info_data

    def get_client_id(self):
        return int(self.get_config_by_value(self.cofigurations_data, CONFIG.CLIENT_ID))

    def get_source_folder_path(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.AUDIO_SOURCE_FOLDER_PATH)

    def get_audio_destination_folder_path(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.AUDIO_DESTINATION_FOLDER_PATH)

    def get_audio_max_file_size(self):
        return int(self.get_config_by_value(self.cofigurations_data, CONFIG.AUDIO_FILE_SIZE))

    def get_audio_chuck_file_size(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.AUDIO_CHUNK_FILE_SIZE)

    def get_whisper_model_name(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.WHISPER_MODEL)

    def get_audio_source_folder_path(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.AUDIO_SOURCE_FOLDER_PATH)

    def get_ladp_user_name(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.LDAP_USER_NAME)

    def get_ldap_user_password(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.LDAP_USER_PASSWORD)

    def get_open_ai_key(self):
        return 'sk-' + self.get_config_by_value(self.cofigurations_data, CONFIG.OPENAI_API_KEY)

    def get_database_server_name(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.DATABASE_SERVER)

    def get_database_name(self):
        return self.get_config_by_value(self.cofigurations_data, CONFIG.DATABASE_NAME)

    def get_all_files(self, path):
        files_arr = []
        arr_all_files = os.listdir(path)
        for file_name in arr_all_files:
            print('file name from folder :- ', file_name)
            file_url = path + "/" + file_name;
            print('Audio File Repo Path : ', file_url)
            #  files_arr.append(file_url)
            files_arr.append(file_name)
        return files_arr

    def delete_file(self, output_file, file_name):
        try:
            file = f"{output_file}/{file_name}"
            os.remove(file)
            for elm_file in os.listdir('.'):
                if elm_file.startswith("file_name") and elm_file.endswith(".txt"):
                    os.remove(elm_file)
        except Exception as e:
            self.logger.error('delete_file', e)

    def delete_files_wishper(self, output_file, chunks_files):
        print('delete_files_wishper console output_file:-  ', output_file)
        for i in range(len(chunks_files)):
            file = f"{output_file}/chunk_{i}.wav"
            print('delete_files_wishper console deleted full file path :-  ', output_file)
            os.remove(file)
        for file in os.listdir(output_file):
            if file.startswith("chunk_") and file.endswith(".txt"):
                os.remove(file)

    def delete_files(self, output_file, chunks_files):
        for i in range(len(chunks_files)):
            file = f"{output_file}/chunk_{i}.wav"
            os.remove(file)
        for file in os.listdir('.'):
            if file.startswith("chunk_") and file.endswith(".txt"):
                os.remove(file)

    def merge_text_files(self, output_file, chunks_files, filename):
        print('merge_text_files')
        txtfile = output_file + '/' + filename + '.txt'
        with open(txtfile, 'w') as outfile:
            for file in os.listdir('.'):
                if file.startswith("chunk_") and file.endswith(".txt"):
                    with open(file, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')
                    print(f"Merged {file}")
        self.delete_files(output_file, chunks_files)

    def convert_text_files(self, output_file, dir_url, file_name):
        print('merge_text_files')
        txt_file = dir_url + '/' + file_name + '.txt'
        with open(txt_file, 'w') as outfile:
            for file in os.listdir('.'):
                if file.startswith('chunk_') and file.endswith(".txt"):
                    with open(file, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')
                    print(f"Merged {file}")
        self.delete_file(dir_url, file_name)

    def merge_text_files(self, output_file, chunks_files, filename):
        print('merge_text_files')
        txt_file = output_file + '/' + filename + '.txt'
        with open(txt_file, 'w') as outfile:
            for file in os.listdir('.'):
                if file.startswith("chunk_") and file.endswith(".txt"):
                    with open(file, 'r') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')
                    print(f"Merged {file}")
        self.delete_files(output_file, chunks_files)

    def merge_files_wishper(self, output_file, chunks_files, filename):
        print('merge_text_files output_file:- ', output_file)
        txtfile = output_file + '/' + filename + '.txt'
        print('merge_text_files txtfile:- ', txtfile)
        with open(txtfile, 'w') as outfile:
            for file in os.listdir(output_file):
                if file.startswith("chunk_") and file.endswith(".txt"):
                    print('merge_text_files file details:- ', file)
                    with open(file, 'r') as infile:
                        # print('merge_text_files infile.read():- ',infile.read())
                        outfile.write(infile.read())
                        outfile.write('\n')
                    print(f"Merged {file}")
        self.delete_files_wishper(output_file, chunks_files)

    def split_audio_chunk_files(self, audio_file, chunk_file_directory):
        try:
            self.logger.info(f'Create Chunk file {audio_file}  file url :- {chunk_file_directory}')
            input_audio = AudioSegment.from_file(audio_file)
            chunk_size = 300000  # 5 minutes
            chunk_files = [input_audio[i:i + chunk_size] for i in range(0, len(input_audio), chunk_size)]
            for i, chunk_paths in enumerate(chunk_files):
                self.logger.info(f"Chunk Split Starting...{str(datetime.now())}")
                chunk_paths.export(f"{chunk_file_directory}/chunk_{i}.wav", bitrate='128k', format="mp3")
            return [chunk_files, chunk_paths]
        except Exception as e:
            self.logger.error(f'Error in Chunking split_audio_chunk_files:- ', e)
            return []

    def create_folder_structure(self, file, source_file_path, destination_path):
        file_url = source_file_path + "/" + file;
        name_file = file_url.split('/')[-1].split('.')[0]
        self.logger.info(f'Audio File name for folder {destination_path} creation : {name_file}')
        try:
            dir_folder_url = os.path.join(destination_path, name_file)
            os.mkdir(dir_folder_url)
            return True
        except Exception as e:
            print(f'caught {type(e)}: e', e)
            return False

    def write_file(self, file_path, transcript):
        try:
            with open(f"{file_path}", "a") as f:
                f.write(transcript["text"])
                return True
        except Exception as e:
            print(f'caught {type(e)}: e', e)
            return False

    def copy_file(self, source_path, destination_path):
        try:
            shutil.copy(source_path, destination_path)
            return True
        except Exception as e:
            print(f'caught {type(e)}: e', e)
            return False

    def wrire_txt_file(self, txt_file_path, transcript):
        try:
            with open(f"{txt_file_path}", "a") as f:
                f.write(transcript["text"])
                self.logger.info(f"Processing stdout123....:  {txt_file_path}")
            return True
        except Exception as e:
            self.logger.error('wrire_txt_file:- ', e)
            return False

    def get_file_extension(self, file):
        try:
            return os.path.splitext(file)
        except Exception as e:
            self.logger.error('get_file_extension', e)

    def get_secret_key(self, user_name):
        # Establish connection with the LDAP server
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
        return token

    def get_config_by_key_name(self, dictionary, target_key):
        for key, value in dictionary.items():
            if key == target_key:
                return value
        return None

    def get_config_by_value(self, dictionary, target_value):
        keys = None
        for dictionary in dictionary:
            for key, value in dictionary.items():
                if value == target_value:
                    for key, value in dictionary.items():
                        if key == "ConfigValue":
                            return value
                    # keys.append(key)
        return keys

    def get_configuration_by_column(self, results):
        filetype_info_column_names = results[0].__dict__.keys() if results else []
        filetype_info_array = [{column: getattr(row, column) for column in filetype_info_column_names} for row in
                               results]
        return filetype_info_array
