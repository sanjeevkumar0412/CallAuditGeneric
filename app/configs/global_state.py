from app.utilities.utility import GlobalUtility
from app.configs.config import CONFIG
class GlobalState:
    _instance = None
    def __init__(self):
        self.global_utility = GlobalUtility()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def get_client_id(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.CLIENT_ID)
    def get_source_folder_path(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.AUDIO_SOURCE_FOLDER_PATH)
    def get_audio_destination_folder_path(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.AUDIO_DESTINATION_FOLDER_PATH)

    def get_audio_max_file_size(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.AUDIO_FILE_SIZE)

    def get_audio_chuck_file_size(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.AUDIO_CHUNK_FILE_SIZE)

    def get_whisper_model_name(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.WHISPER_MODEL)

    def get_audio_source_folder_path(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.AUDIO_SOURCE_FOLDER_PATH)

    def get_ladp_user_name(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.LDAP_USER_NAME)

    def get_ldap_user_password(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.LDAP_USER_PASSWORD)

    def get_open_ai_key(self):
        return 'sk-'+self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.OPENAI_API_KEY)

    def get_database_server_name(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.DATABASE_SERVER)

    def get_database_name(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(), CONFIG.DATABASE_NAME)