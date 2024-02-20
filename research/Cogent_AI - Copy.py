import whisper
from pydub import AudioSegment
import subprocess
import shutil
import os
from datetime import datetime

def delete_files(output_file,chunkFiles):
    for i in range(len(chunkFiles)):
        file = f"{output_file}/chunk_{i}.wav"
        os.remove(file)
    for file in os.listdir('.'):
        if file.startswith("chunk_") and file.endswith(".txt"):
            os.remove(file)

def merge_text_files(output_file,chunkFiles,filename):
    print('merge_text_files')
    txtfile = output_file+'/'+filename+'.txt'
    with open(txtfile, 'w') as outfile:
        for file in os.listdir('.'):
            if file.startswith("chunk_") and file.endswith(".txt"):
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_files(output_file,chunkFiles)   
    


def transcribe_chunk(chunksFiles,chunkDirectory,chunks,filename):
   for i in range(len(chunksFiles)):
    # with open('D:/GitRepo/LargeFiles/Interview1.txt', 'w') as fd:
        chunk_file = f"{chunkDirectory}/chunk_{i}.wav"
        # Launch a subprocess to transcribe the audio chunk
        print("subprocess Start...", str(datetime.now()))
        # process = subprocess.run(["whisper", chunk_file, "--model", "base","--language", "en", "--output_format", "txt"],shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["whisper", chunk_file, "--model", "base","--language", "en", "--output_format", "txt"])
        # stdout, stderr = process.communicate()
        # print(stdout.decode(), stderr.decode())
        # print("Processing stderr.decode()....:  ",stderr.decode())
        # print("Processing stdout....:  ",stdout.decode())
        print("Processing stdout....:  ",filename)
        
        # subprocess.Popen(["python", "transcribe_script.py", chunk_file])
   merge_text_files(chunkDirectory,chunks,filename)

def delete_file(output_file,file_name):    
    file = f"{output_file}/{file_name}"
    os.remove(file)
    for elm_File in os.listdir('.'):
        if elm_File.startswith("file_name") and elm_File.endswith(".txt"):
            os.remove(elm_File)

def convert_text_files(output_file,dir_FolderUrl,file_name):
    print('merge_text_files')
    txtfile = dir_FolderUrl+'/'+file_name+'.txt'
    with open(txtfile, 'w') as outfile:
        for file in os.listdir('.'):
            if file.startswith(file_name) and file.endswith(".txt"):
                with open(file, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')
                print(f"Merged {file}")  
    delete_file(dir_FolderUrl,file_name)   

def transcribe(output_file,dir_FolderUrl,name):
    model = whisper.load_model("base")
    result = model.transcribe(output_file)
    txtFile = os.path.join(dir_FolderUrl, name)
    with open(f"{txtFile}.txt","w") as f:
        f.write(result["text"]) 
        # print("subprocess Start...", str(datetime.now()))        
        # subprocess.run(["whisper", output_file, "--model", "base","--language", "en", "--output_format", "txt"])
        # convert_text_files(output_file,dir_FolderUrl,name)

def create_chunk_file(audioFile, chunkFileDirectory,fName):
    print('chunk file url :- ',audioFile)
    print('chunk file Folder :- ',chunkFileDirectory)
    input_audio = AudioSegment.from_file(audioFile)    
    chunk_size = 300000 #5 minutes    
    chunks = [input_audio[i:i+chunk_size] for i in range(0, len(input_audio), chunk_size)]   
    for i, chunk in enumerate(chunks):
        print("Chunk Split Start...", str(datetime.now()))
        chunk.export(f"{chunkFileDirectory}/chunk_{i}.wav", bitrate='128k',format="mp3")
    transcribe_chunk(chunks,chunkFileDirectory,chunks,fName)

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
        # shutil.copyfile(fileUrl, os.path.join(folder_dir, name))
        shutil.copy(fileUrl, dirFolderUrl)
        file_size = os.path.getsize(os.path.join(dirFolderUrl, fileName))
        file_size_mb = file_size / (1024 * 1024)
        audioFilePath = os.path.join(dirFolderUrl, fileName)
        if file_size_mb > 5 :
            print('file size :- ',file_size_mb)            
            create_chunk_file(audioFilePath,dirFolderUrl,nameFile)
        else :            
            print('file size is small from 10m mbs :- ',file_size_mb)
            print('audioFilePath:- ',audioFilePath)
            print('dirFolderUrl:- ',dirFolderUrl)
            print('nameFile:- ',nameFile)
            transcribe(audioFilePath,dirFolderUrl,nameFile)
     except FileExistsError:   
        print('path of Destination: ',"D:\Cogent_AI_Audio_Repo\CallRecording10")


     