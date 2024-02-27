import whisper 
import openai
from pydub import AudioSegment
import subprocess
import shutil
import os
from datetime import datetime
import time
from openai import OpenAI
import speech_recognition as sr
from app.services.logger import Logger

class TranscribeAudio:  
# place keys here
    _instance = None

    def __init__(self):        
        self.logger = Logger.get_instance()
       

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def transcribe(self,output_file,dir_url,name):
        model = whisper.load_model("tiny")
        result = model.transcribe(output_file)
        txt_file = os.path.join(dir_url, name)
        with open(f"{txt_file}.txt","w") as f:
            f.write(result["text"])

    

    

      


   