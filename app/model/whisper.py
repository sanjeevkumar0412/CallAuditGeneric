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
from app.utilities.utility import GlobalUtility

class WhisperModel: 
    # global_utility =  GlobalUtility()       
    def __init__(self):
        # self.model = model
        self.global_utility =  GlobalUtility()

    def whisper_transcribe_small_audio(self,file_path,model_name ="tiny"):
        model = whisper.load_model(model_name)
        result = model.transcribe(file_path)
        return result
        # txt_file = os.path.join(dir_url, name)
        # with open(f"{txt_file}.txt","w") as f:
        #     f.write(result["text"])

    def whisper_transcribe_large_audio(self,file_path,model_name ="tiny"):       
            model = whisper.load_model(model_name)
            try: 
                # txt_file = chunk_directory+'/'+filename+'.txt'
                # for i in range(len(chunks_files)):   
                    # chunk_file = f"{chunk_directory}/chunk_{i}.wav"
                    result = model.transcribe(file_path)
                    # self.global_utility.delete_files_wishper(chunk_directory,chunks)
                    return  result
                        # file_path = os.path.join(chunk_directory, f"chunk_{i}") 
                        # with open(f"{file_path}.txt","w") as f:
                        # with open(f"{txt_file}","a") as f:
                        #     f.write(result["text"]) 
                        # print("Processing stdout....:  ",filename)
                        # os.remove(chunk_file)  
                
                # merge_files_wishper(chunk_directory,chunks,filename)
            except Exception as e:
                        # print(f"Error transcribing {filename}: {e}")
                        print(f"Error transcribing : {e}")
                        self.retries_model(file_path)                   

    def retries_model(self,failed_file):           
            retries =3
            model = whisper.load_model("tiny")
            for attempt in range(retries):
                try:
                    print('fialed file process start : ',failed_file)
                    time.sleep(2**attempt)
                    result = model.transcribe(failed_file)
                    return result
                    # with open(f"{output_file}","a") as f:
                    #     f.write(result["text"])
                    # print('Failed file Status: ',failed_file)
                    # os.remove(failed_file) 
                    break  
                except Exception as e:
                    print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")
            else:
                print(f"Giving up on {failed_file} after {retries} attempts")    