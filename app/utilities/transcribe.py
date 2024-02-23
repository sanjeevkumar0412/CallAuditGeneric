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


class TranscribeAudio:  
# place keys here
    def __init__(self):
        self.client = OpenAI()
        # self.model = model     

    def transcribe(self,output_file,dir_url,name):
        model = whisper.load_model("tiny")
        result = model.transcribe(output_file)
        txt_file = os.path.join(dir_url, name)
        with open(f"{txt_file}.txt","w") as f:
            f.write(result["text"])

    

    

      


   