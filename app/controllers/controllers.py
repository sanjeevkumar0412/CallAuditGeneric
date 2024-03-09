# controller.py
from app.model.open_ai import OpenAIModel
from app.model.whisper import WhisperModel
from app.model.subprocess_model import SubProcessModel
from app.services.logger import Logger


class Controller:
    _instance = None
    def __init__(self):
        super().__init__()
        self.open_ai_model = OpenAIModel()
        self.whisper_model = WhisperModel()
        self.sub_process_model = SubProcessModel()
        self.logger = Logger()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def build_chunk_files_transcribe_audio(self, chunks_files, subscriptions_model=None):
        transcript = None
        try:
            if subscriptions_model == "Premium":
                transcript = self.open_ai_model.open_ai_transcribe_large_audio(chunks_files)
                self.logger.info("Get the logger information from here!12")
            elif subscriptions_model == "Small":
                transcript = self.whisper_model.whisper_transcribe_large_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!66")
            elif subscriptions_model == "Normal":
                transcript = self.open_ai_model.open_ai_transcribe_large_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!12qw")
            else:
                transcript = self.open_ai_model.open_ai_transcribe_large_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!12qwsdfdf")
            return transcript
        except Exception as e:
            print('Error while creating build_transcribe_model', e)
            self.build_chunk_files_transcribe_audio(chunks_files, subscriptions_model)

    def build_transcribe_audio(self, chunks_files, subscriptions_model=None):
        transcript = ''
        try:
            if subscriptions_model == "Premium":
                transcript = self.open_ai_model.open_ai_transcribe_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!12")
            elif subscriptions_model == "Small":
                transcript = self.whisper_model.whisper_transcribe_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!66")
            elif subscriptions_model == "Normal":
                transcript = self.open_ai_model.open_ai_model.open_ai_transcribe_small_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!12qw")
            else:
                transcript = self.open_ai_model.open_ai_transcribe_audio(chunks_files, "tiny")
                self.logger.info("Get the logger information from here!12qwsdfdf")
            return transcript
        except Exception as e:
            print('Error while creating build_transcribe_model', e)
            self.build_chunk_files_transcribe_audio(chunks_files, subscriptions_model)

    def get_open_ai_transcribe_large_audio(self, chunks_files, chunk_directory, chunks, filename):
        transcript = self.open_ai_model.open_ai_transcribe_large_audio(chunks_files, chunk_directory, chunks, filename)
        self.logger.info("Get the logger information from here!")
        return transcript

    def get_open_ai_transcribe_large_audio(self, chunks_files, chunk_directory, chunks, filename):
        transcript = self.open_ai_model.open_ai_transcribe_audio(chunks_files, chunk_directory, chunks, filename)
        self.logger.info("Get the logger information from here!")
        return transcript
