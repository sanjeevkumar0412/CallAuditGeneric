import time
import os
from openai import OpenAI

from app.utilities.utility import GlobalUtility
from app.services.logger import Logger
client = OpenAI()

# place keys here
def open_ai_transcribe_audio(transcribe_file, model="whisper-1"):
    try:
        print(' Open Ai Audio File Path', transcribe_file)
        audio_file = open(transcribe_file, "rb")
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file
        )
        print(transcript)
    except Exception as e:
        print(f"Error transcribing : {e}")
        return retries_model(transcribe_file)


def retries_model(failed_file):
        retries =3
        for attempt in range(retries):
            try:
                print('fialed file process start : ',failed_file)
                time.sleep(2**attempt)
                audio_file= open(failed_file, "rb")
                transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format='text'
                                )
                return transcript
                # break
            except Exception as e:
                print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")