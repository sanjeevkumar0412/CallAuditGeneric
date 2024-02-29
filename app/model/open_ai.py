import openai
from pydub import AudioSegment
import os
from datetime import datetime
import time
from openai import OpenAI

from app.utilities.utility import GlobalUtility
from app.services.logger import Logger

# place keys here

class OpenAIModel:
    _instance = None        
    def __init__(self):        
        self.global_utility =  GlobalUtility.get_instance()
        self.logger = Logger.get_instance()
        self.client = OpenAI()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def open_ai_transcribe_audio(self,transcribe_file,model = "whisper-1"):
        try:
            print(' Open Ai Audio File Path',transcribe_file)
            audio_file= open(transcribe_file, "rb") 
            transcript = self.client.audio.transcriptions.create(
                                    model=model, 
                                    file=audio_file                         
                                    )
            print(transcript)
        except Exception as e:
                        print(f"Error transcribing : {e}")                       
                        return self.retries_model(transcribe_file)

    def open_ai_transcribe_large_audio(self,chunk_file,model = "whisper-1"):   
            try:               
                print(' Open Ai Chunk Audio File Path',chunk_file)
                audio_file= open(chunk_file, "rb") 
                transcript = self.client.audio.transcriptions.create(
                            model=model, 
                            file=audio_file,
                            response_format='text'                                                           
                            )
                return transcript  
            except Exception as e:
                        print(f"Error transcribing : {e}")                       
                        return self.retries_model(chunk_file) 

    def retries_model(self,failed_file):           
            retries =3           
            for attempt in range(retries):
                try:
                    print('fialed file process start : ',failed_file)
                    time.sleep(2**attempt)
                    audio_file= open(failed_file, "rb") 
                    transcript = self.client.audio.transcriptions.create(
                                    model="whisper-1", 
                                    file=audio_file,
                                    response_format='text'                                                           
                                    )
                    return transcript
                    # break  
                except Exception as e:
                    print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")             