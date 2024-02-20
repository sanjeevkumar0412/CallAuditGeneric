import whisper 
from pydub import AudioSegment
import subprocess
import shutil
import os
from datetime import datetime


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

def transcribe_by_whisper(chunks_files,chunk_directory,chunks,filename):
   model = whisper.load_model("tiny")
   txt_file = chunk_directory+'/'+filename+'.txt'
   for i in range(len(chunks_files)):   
        chunk_file = f"{chunk_directory}/chunk_{i}.wav"
        result = model.transcribe(chunk_file)
        # file_path = os.path.join(chunk_directory, f"chunk_{i}")
        # with open(f"{file_path}.txt","w") as f:
        with open(f"{txt_file}","a") as f:
            f.write(result["text"]) 
        print("Processing stdout....:  ",filename)  
   delete_files_wishper(chunk_directory,chunks)
#    merge_files_wishper(chunk_directory,chunks,filename)
   
def transcribe_by_subprocess(chunks_files,chunk_directory,chunks,filename):   
   for i in range(len(chunks_files)):   
        chunk_file = f"{chunk_directory}/chunk_{i}.wav"          
        print("subprocess Start...", str(datetime.now()))       
        subprocess.run(["whisper", chunk_file, "--model", "base","--language", "en", "--output_format", "txt"])        
        print("Processing stdout....:  ",filename)  
   merge_text_files(chunk_directory,chunks,filename)