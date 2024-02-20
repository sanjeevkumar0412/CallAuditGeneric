import whisper
from pydub import AudioSegment
import subprocess
import shutil
import os
from datetime import datetime

def delete_files(output_file,chunks_files):
    for i in range(len(chunks_files)):
        file = f"{output_file}/chunk_{i}.wav"
        os.remove(file)
    for file in os.listdir('.'):
        if file.startswith("chunk_") and file.endswith(".txt"):
            os.remove(file)

def delete_files_wishper(output_file,chunks_files):
    for i in range(len(chunks_files)):
            file = f"{output_file}/chunk_{i}.wav"            
            os.remove(file)
    for file in os.listdir(output_file):
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


def transcribe_by_subprocess(chunks_files,chunk_directory,chunks,filename):   
   for i in range(len(chunks_files)):   
        chunk_file = f"{chunk_directory}/chunk_{i}.wav"          
        print("subprocess Start...", str(datetime.now()))       
        subprocess.run(["whisper", chunk_file, "--model", "base","--language", "en", "--output_format", "txt"])        
        print("Processing stdout....:  ",filename)  
   merge_text_files(chunk_directory,chunks,filename)

def transcribe_by_whisper(chunks_files,chunk_directory,chunks,filename):
   model = whisper.load_model("base")
   txt_file = chunk_directory+'/'+filename+'.txt'
   for i in range(len(chunks_files)):   
        chunk_file = f"{chunk_directory}/chunk_{i}.wav"
        result = model.transcribe(chunk_file)
        file_path = os.path.join(chunk_directory, f"chunk_{i}")
        # with open(f"{file_path}.txt","w") as f:
        with open(f"{txt_file}","a") as f:
            f.write(result["text"]) 
        print("Processing stdout....:  ",filename)  
   merge_files_wishper(chunk_directory,chunks,filename)
        
def delete_file(output_file,file_name):    
    file = f"{output_file}/{file_name}"
    os.remove(file)
    for elm_file in os.listdir('.'):
        if elm_file.startswith("file_name") and elm_file.endswith(".txt"):
            os.remove(elm_file)

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
    model = whisper.load_model("base")
    result = model.transcribe(output_file)
    txt_file = os.path.join(dir_url, name)
    with open(f"{txt_file}.txt","w") as f:
        f.write(result["text"])         

def create_chunk_subprocess_file(audio_file, chunk_file_directory,f_name):
    print('chunk file url :- ',audio_file)
    print('chunk file Folder :- ',chunk_file_directory)
    input_audio = AudioSegment.from_file(audio_file)    
    chunk_size = 300000 #5 minutes    
    chunks = [input_audio[i:i+chunk_size] for i in range(0, len(input_audio), chunk_size)]   
    for i, chunk in enumerate(chunks):
        print("Chunk Split Start...", str(datetime.now()))
        chunk.export(f"{chunk_file_directory}/chunk_{i}.wav", bitrate='128k',format="mp3")
    transcribe_by_whisper(chunks,chunk_file_directory,chunks,f_name)
    # transcribe_by_subprocess(chunks,chunkFileDirectory,chunks,fName)

sourceFilePath ="D:/Cogent_Audio_Repo/"
destination_folder = "D:/Cogent_AI_Audio_Repo"
arrAllFiles = dir_list = os.listdir(sourceFilePath)
filesArr = []
for fileName in arrAllFiles:
     print('file path :- ',fileName)
     fileUrl = sourceFilePath+"/"+fileName;
     print('Audio File Repo Path : ',fileUrl)
    #  filesArr.append(fileUrl)
     nameFile =fileUrl.split('/')[-1].split('.')[0] 
     print('Audio File name : ',nameFile)     
     try:
        dirFolderUrl = os.path.join(destination_folder, nameFile)
        os.mkdir(dirFolderUrl) 
        print('Source Audio File Path : -' ,fileUrl)
        print('Source Normal Path Audio File Path : -' ,os.path.normpath(fileUrl))
        print('Destination Audio File Path : -' , os.path.normpath(sourceFilePath))       
        shutil.copy(fileUrl, dirFolderUrl)
        file_size = os.path.getsize(os.path.join(dirFolderUrl, fileName))
        file_size_mb = file_size / (1024 * 1024)
        audioFilePath = os.path.join(dirFolderUrl, fileName)
        if file_size_mb > 5 :
            print('file size :- ',file_size_mb)                       
            create_chunk_subprocess_file(audioFilePath,dirFolderUrl,nameFile)
        else :            
            print('file size is small from 10m mbs :- ',file_size_mb)
            print('audioFilePath:- ',audioFilePath)
            print('dirFolderUrl:- ',dirFolderUrl)
            print('nameFile:- ',nameFile)
            # transcribe(audioFilePath,dirFolderUrl,nameFile)
     except FileExistsError:   
        print('path of Destination: ',"D:\Cogent_AI_Audio_Repo\CallRecording10")


     