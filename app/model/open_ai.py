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

# place keys here
client = OpenAI()
class OpenAIModel:        
    def __init__(self):
        # self.model = model
        self.global_utility =  GlobalUtility.get_instance()

    def open_ai_transcribe_small_audio(self,output_file,dir_url,name):
        print(' Open Ai Audio File Path',output_file)
        audio_file= open(output_file, "rb") 
        transcript = client.audio.transcriptions.create(
                                model="whisper-1", 
                                file=audio_file                         
                                )
        print(transcript)
        txt_file = os.path.join(dir_url, name)
        print('result["text"]',transcript["text"])
        with open(f"{txt_file}.txt","w") as f:
            # f.write(result)
            f.write(transcript["text"])

    def open_ai_transcribe_large_audio_old(self,chunks_files,chunk_directory,chunks,filename):   
            try: 
                txt_file = chunk_directory+'/'+filename+'.txt'
                for i in range(len(chunks_files)):   
                        chunk_file = f"{chunk_directory}/chunk_{i}.wav"
                        print(' Open Ai Chunk Audio File Path',chunk_file)
                        recognizer = sr.Recognizer()
                        audio = sr.AudioFile(chunk_file)  
                        with audio as source:
                            audio_data = recognizer.record(source)
                        transcribed_text = recognizer.recognize_google(audio_data)
                        response = openai.Completion.create(engine="text-davinci-003", prompt=transcribed_text, max_tokens=100)
                        final_text = response.choices[0].text.strip()
                        print("Final transcribed text:")
                        print(final_text)                     
                self.global_utility.delete_files_wishper(chunk_directory,chunks)
                # merge_files_wishper(chunk_directory,chunks,filename)
            except Exception as e:
                        print(f"Error transcribing {filename}: {e}")
                        self.retries_model(txt_file,chunk_file) 

    def open_ai_transcribe_large_audio(self,chunk_file,model = "whisper-1"):   
            try: 
                # txt_file = chunk_directory+'/'+filename+'.txt'
                # for i in range(len(chunks_files)):   
                # chunk_file = f"{chunk_directory}/chunk_{i}.wav"
                print(' Open Ai Chunk Audio File Path',chunk_file)
                audio_file= open(chunk_file, "rb") 
                transcript = client.audio.transcriptions.create(
                            model=model, 
                            file=audio_file,
                            response_format='text'                                                           
                            )
                return transcript
                        # file_path = os.path.join(chunk_directory, f"chunk_{i}") 
                        # with open(f"{file_path}.txt","w") as f:
                        # print(transcript["text"])
                        # print('result["text"]',result["text"])
                        # with open(f"{txt_file}","a") as f:
                        #     # f.write(result) 
                        #     f.write(transcript["text"]) 
                        # print("Processing stdout123....:  ",filename)
                        # os.remove(chunk_file)  
                self.global_utility.delete_files_wishper(chunk_directory,chunks)
                # merge_files_wishper(chunk_directory,chunks,filename)
            except Exception as e:
                        print(f"Error transcribing : {e}")
                        # print(f"Error transcribing {filename}: {e}")
                        # self.retries_model(txt_file,chunk_file) 

    def retries_model(self,output_file,failed_file):           
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
                    with open(f"{output_file}","a") as f:
                        f.write(transcript["text"])
                    print('Failed file Status: ',failed_file)
                    os.remove(failed_file) 
                    break  
                except Exception as e:
                    print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")
            else:
                print(f"Giving up on {failed_file} after {retries} attempts")  