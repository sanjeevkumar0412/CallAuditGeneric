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

def delete_file(output_file,file_name):    
    file = f"{output_file}/{file_name}"
    os.remove(file)
    for elm_file in os.listdir('.'):
        if elm_file.startswith("file_name") and elm_file.endswith(".txt"):
            os.remove(elm_file)

def delete_files_wishper(output_file,chunks_files):
    print('delete_files_wishper console output_file:-  ',output_file)
    for i in range(len(chunks_files)):
            file = f"{output_file}/chunk_{i}.wav" 
            print('delete_files_wishper console deleted full file path :-  ',output_file)           
            os.remove(file)
    for file in os.listdir(output_file):
        if file.startswith("chunk_") and file.endswith(".txt"):
            os.remove(file)

def delete_files(output_file,chunks_files):
    for i in range(len(chunks_files)):
        file = f"{output_file}/chunk_{i}.wav"
        os.remove(file)
    for file in os.listdir('.'):
        if file.startswith("chunk_") and file.endswith(".txt"):
            os.remove(file)

def merge_text_files(output_file,chunks_files,filename):
    print('merge_text_files')
    txtfile = output_file+'/'+filename+'.txt'
    with open(txtfile, 'w') as outfile:
        for file in os.listdir('.'):
            if file.startswith("chunk_") and file.endswith(".txt"):
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_files(output_file,chunks_files) 

def convert_text_files(output_file,dir_url,file_name):
    print('merge_text_files')
    txtfile = dir_url+'/'+file_name+'.txt'
    with open(txtfile, 'w') as outfile:
        for file in os.listdir('.'):
            if file.startswith('chunk_') and file.endswith(".txt"):
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_file(dir_url,file_name)   

def transcribe(output_file,dir_url,name):
    model = whisper.load_model("tiny")
    result = model.transcribe(output_file)
    txt_file = os.path.join(dir_url, name)
    with open(f"{txt_file}.txt","w") as f:
        f.write(result["text"])

def merge_text_files(output_file,chunks_files,filename):
    print('merge_text_files')
    txtfile = output_file+'/'+filename+'.txt'
    with open(txtfile, 'w') as outfile:
        for file in os.listdir('.'):
            if file.startswith("chunk_") and file.endswith(".txt"):
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_files(output_file,chunks_files)

def merge_files_wishper(output_file,chunks_files,filename):
    print('merge_text_files output_file:- ',output_file)
    txtfile = output_file+'/'+filename+'.txt'
    print('merge_text_files txtfile:- ',txtfile)
    with open(txtfile, 'w') as outfile:
        for file in os.listdir(output_file):
            if file.startswith("chunk_") and file.endswith(".txt"):
                print('merge_text_files file details:- ',file)
                with open(file, 'r') as infile:
                    # print('merge_text_files infile.read():- ',infile.read())
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_files_wishper(output_file,chunks_files)

def retries_model(output_file,failed_file):
        retries =3
        model = whisper.load_model("tiny")
        for attempt in range(retries):
            try:
                print('fialed file process start : ',failed_file)
                time.sleep(2**attempt)             
                result = model.transcribe(failed_file)
                with open(f"{output_file}","a") as f:
                    f.write(result["text"])
                print('Failed file Status: ',failed_file)
                os.remove(failed_file) 
                break  
            except Exception as e:
                print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")
        else:
            print(f"Giving up on {failed_file} after {retries} attempts")   

def transcribe_open_ai(output_file,dir_url,name):
    print(' Open Ai Audio File Path',output_file)
    audio_file= open(output_file, "rb") 
    transcript = client.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file                         
                            )
    print(transcript)
    # txt_file = os.path.join(dir_url, name)
    # print('result["text"]',result["text"])
    # with open(f"{txt_file}.txt","w") as f:
    #     # f.write(result)
    #     f.write(result["text"])

def transcribe_by_open_ai_old(chunks_files,chunk_directory,chunks,filename):   
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

def transcribe_by_open_ai(chunks_files,chunk_directory,chunks,filename):   
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
                    # with open(f"{txt_file}","a") as f:
                    #     # f.write(result) 
                    #     f.write(result["text"]) 
                    print("Processing stdout123....:  ",filename)
                    # os.remove(chunk_file)  
            delete_files_wishper(chunk_directory,chunks)
            # merge_files_wishper(chunk_directory,chunks,filename)
        except Exception as e:
                    print(f"Error transcribing {filename}: {e}")
                    retries_model(txt_file,chunk_file) 

def transcribe_by_whisper(chunks_files,chunk_directory,chunks,filename):       
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
        
   
def transcribe_by_subprocess(chunks_files,chunk_directory,chunks,filename):   
   for i in range(len(chunks_files)):   
        chunk_file = f"{chunk_directory}/chunk_{i}.wav"          
        print("subprocess Start...", str(datetime.now()))       
        subprocess.run(["whisper", chunk_file, "--model", "base","--language", "en", "--output_format", "txt"])        
        print("Processing stdout....:  ",filename)  
   merge_text_files(chunk_directory,chunks,filename)