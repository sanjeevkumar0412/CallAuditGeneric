# controller.py
from app.model.open_ai import OpenAIModel
from app.model.whisper import WhisperModel
from app.model.subprocess_model import SubProcessModel
from app.utilities.logger import AppLogger
class UserController(AppLogger):
    def __init__(self):
        super().__init__()
        self.open_ai_model = OpenAIModel()
        self.whisper_model = WhisperModel()
        self.sub_process_model = SubProcessModel()

    def get_open_ai_transcribe_large_audio(self,chunks_files,chunk_directory,chunks,filename):
        transcript = self.open_ai_model.open_ai_transcribe_large_audio(self,chunks_files,chunk_directory,chunks,filename)
        self.logger.info("Get the logger information from here!")
        return transcript