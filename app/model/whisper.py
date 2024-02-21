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


def whisper_transcribe_small_audio(output_file,dir_url,name):
    model = whisper.load_model("tiny")
    result = model.transcribe(output_file)
    txt_file = os.path.join(dir_url, name)
    with open(f"{txt_file}.txt","w") as f:
        f.write(result["text"])

def whisper_transcribe_large_audio(chunks_files,chunk_directory,chunks,filename):       
        model = whisper.load_model("tiny")
        try: 
            txt_file = chunk_directory+'/'+filename+'.txt'
            for i in range(len(chunks_files)):   
                    chunk_file = f"{chunk_directory}/chunk_{i}.wav"
                    result = model.transcribe(chunk_file)
                    # file_path = os.path.join(chunk_directory, f"chunk_{i}") 
                    # with open(f"{file_path}.txt","w") as f:
                    with open(f"{txt_file}","a") as f:
                        f.write(result["text"]) 
                    print("Processing stdout....:  ",filename)
                    # os.remove(chunk_file)  
            delete_files_wishper(chunk_directory,chunks)
            # merge_files_wishper(chunk_directory,chunks,filename)
        except Exception as e:
                    print(f"Error transcribing {filename}: {e}")
                    retries_model(txt_file,chunk_file)                   
        