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


# place keys here
client = OpenAI()

def open_ai_transcribe_small_audio(output_file,dir_url,name):
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

def open_ai_transcribe_large_audio_old(chunks_files,chunk_directory,chunks,filename):   
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
            delete_files_wishper(chunk_directory,chunks)
            # merge_files_wishper(chunk_directory,chunks,filename)
        except Exception as e:
                    print(f"Error transcribing {filename}: {e}")
                    retries_model(txt_file,chunk_file) 

def open_ai_transcribe_large_audio(chunks_files,chunk_directory,chunks,filename):   
        try: 
            txt_file = chunk_directory+'/'+filename+'.txt'
            for i in range(len(chunks_files)):   
                    chunk_file = f"{chunk_directory}/chunk_{i}.wav"
                    print(' Open Ai Chunk Audio File Path',chunk_file)
                    audio_file= open(chunk_file, "rb") 
                    transcript = client.audio.transcriptions.create(
                                model="whisper-1", 
                                file=audio_file,
                                response_format='text'                                                           
                                )
                    # file_path = os.path.join(chunk_directory, f"chunk_{i}") 
                    # with open(f"{file_path}.txt","w") as f:
                    print(transcript["text"])
                    # print('result["text"]',result["text"])
                    with open(f"{txt_file}","a") as f:
                        # f.write(result) 
                        f.write(transcript["text"]) 
                    print("Processing stdout123....:  ",filename)
                    # os.remove(chunk_file)  
            delete_files_wishper(chunk_directory,chunks)
            # merge_files_wishper(chunk_directory,chunks,filename)
        except Exception as e:
                    print(f"Error transcribing {filename}: {e}")
                    retries_model(txt_file,chunk_file) 
