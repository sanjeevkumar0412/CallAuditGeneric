from app.utilities.utility import GlobalUtility
from app.configs.config import  CONFIG
class GlobalState:
    _instance = None
    def __init__(self):
        self.global_utility = GlobalUtility().get_instance()
        self.audio_source_path = None


    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def get_source_folder_path(self):
        return self.global_utility.get_config_by_value(self.global_utility.get_cofigurations_data(),CONFIG.SOURCE_FOLDER_PATH)