import whisper 
from pydub import AudioSegment
import subprocess
from dotenv import load_dotenv
import shutil
import os
from datetime import datetime
from app.utilities.transcribe import transcribe,transcribe_by_whisper,transcribe_by_open_ai,transcribe_open_ai

load_dotenv()

def get_all_files(path):
    files_arr = []
    arr_all_files  = os.listdir(path)
    for file_name in arr_all_files:
       print('file name from folder :- ',file_name)
       file_url = path+"/"+file_name;
       print('Audio File Repo Path : ',file_url)
      #  files_arr.append(file_url)
       files_arr.append(file_name)
    return  files_arr

def split_audio_chunk_files(audio_file, chunk_file_directory,f_name,is_open_ai_model=False):
     print('create_chunk_subprocess_file chunk file url :- ',audio_file)
     print('create_chunk_subprocess_file chunk file Folder :- ',chunk_file_directory)
     input_audio = AudioSegment.from_file(audio_file) 
     chunk_size = 300000 #5 minutes
   #   chunk_size = os.getenv('chunk_size')  
   #   chunk_size =  os.environ['chunk_size'] 
    #  300000 #5 minutes    
     chunks = [input_audio[i:i+chunk_size] for i in range(0, len(input_audio), chunk_size)]   
     for i, chunk in enumerate(chunks):
        print("Chunk Split Start...", str(datetime.now()))
        chunk.export(f"{chunk_file_directory}/chunk_{i}.wav", bitrate='128k',format="mp3")
     if is_open_ai_model:
         print('Model Open AI is Working...')  
         transcribe_by_open_ai(chunks,chunk_file_directory,chunks,f_name)
     else:
           print('Model Whishper is Working...')
           transcribe_by_whisper(chunks,chunk_file_directory,chunks,f_name)  
    # transcribe_by_subprocess(chunks,chunkFileDirectory,chunks,fName)

def create_folder_structure(files_arr,source_file_path,destination_path,is_open_ai_model=False):
   #   destination_folder =  os.getenv('destination_folder'),
   #   source_file_path = os.getenv('source_file_path'),
   #   destination_folder = os.environ['destination_folder']
   #   source_file_path = os.environ['sourceFilePath'] 
     print('source_file_path path:- ',source_file_path)
     print('destination_folder path:- ',destination_path)
     for file in files_arr:
         file_url = source_file_path+"/"+file;
         name_file =file_url.split('/')[-1].split('.')[0]
         print('Audio File name for folder creation : ',name_file) 
         try:
             dir_folder_url = os.path.join(destination_path, name_file)
             os.mkdir(dir_folder_url) 
             print('Source Audio File Path file : -' ,file)
             print('Source Normal Path Audio File Path file : -' ,file)
             print('Destination Audio File Path source_file_path : -' , source_file_path)
             print('dir_folder_url Audio File Path dir_folder_url : -' , dir_folder_url)        
             shutil.copy(file_url, dir_folder_url)
             file_size = os.path.getsize(os.path.join(dir_folder_url, file))
            #  file_size = os.path.getsize(dir_folder_url)
             file_size_mb = file_size / (1024 * 1024)
             audio_file_path = os.path.join(dir_folder_url, file)
             print('audio_file_path Audio File Path audio_file_path : -' , audio_file_path)
             if file_size_mb > 5 :
                print('file size :- ',file_size_mb)                       
                split_audio_chunk_files(audio_file_path,dir_folder_url,name_file,is_open_ai_model)
             else :            
                print('file size is small from 10m mbs :- ',file_size_mb)
                print('audioFilePath:- ',audio_file_path)
                print('dirFolderUrl:- ',dir_folder_url)
                print('nameFile:- ',name_file)
                if is_open_ai_model :
                   print('Model Open AI is Working for small files...')
                   transcribe_open_ai(audio_file_path,dir_folder_url,name_file)
                else:
                  print('Model Whishper is Working for small file...')
                  transcribe(audio_file_path,dir_folder_url,name_file)
         except Exception as e:   
                  print(f'caught {type(e)}: e',e)