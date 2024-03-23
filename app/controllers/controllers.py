# controller.py
from app.model.open_ai_model import open_ai_transcribe_audio
from app.model.offline_model import retries_model_offline,whisper_transcribe_audio



def build_chunk_files_transcribe_audio(self, chunks_files, subscriptions_model=None):
    transcript = None
    try:
        if subscriptions_model == "Premium":
            transcript = open_ai_transcribe_audio(chunks_files)
            self.logger.info("Get the logger information from here!12")
        elif subscriptions_model == "Small":
            transcript = retries_model_offline(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!66")
        elif subscriptions_model == "Normal":
            transcript = open_ai_transcribe_audio(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!12qw")
        else:
            transcript = open_ai_transcribe_audio(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!12qwsdfdf")
        return transcript
    except Exception as e:
        print('Error while creating build_transcribe_model', e)
        self.build_chunk_files_transcribe_audio(chunks_files, subscriptions_model)


def build_transcribe_audio(self, chunks_files, subscriptions_model=None):
    transcript = ''
    try:
        if subscriptions_model == "Premium":
            transcript = open_ai_transcribe_audio(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!12")
        elif subscriptions_model == "Small":
            transcript = whisper_transcribe_audio(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!66")
        elif subscriptions_model == "Normal":
            transcript = whisper_transcribe_audio(chunks_files, "tiny")
            self.logger.info("Get the logger information from here!12qw")
        else:
            transcript = whisper_transcribe_audio(chunks_files, "tiny")
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

