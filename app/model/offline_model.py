import whisper 
import time
from app.utilities.utility import GlobalUtility
from app.services.logger import Logger


def whisper_transcribe_audio(file_path, model_name="basic"):
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path)
        return result
    except Exception as e:
        print(f"Error transcribing : {e}")
        retries_model_offline(file_path, model_name)


def retries_model_offline(failed_file, model_name):
    retries = 3
    model = whisper.load_model(model_name)
    for attempt in range(retries):
        try:
            print('fialed file process start : ', failed_file)
            time.sleep(2 ** attempt)
            result = model.transcribe(failed_file)
            return result
            # break
        except Exception as e:
            print(f"Failed to transcribe {failed_file} even after {attempt + 1} attempt(s): {e}")
