import os
from dotenv import load_dotenv
from app.model.transcribe_model import build_transcribe_model

load_dotenv()

# api_key = os.getenv('source_file_path')
# secret_key = os.getenv('destination_folder')
# print('api_key path:- ',api_key)
# print('secret_key path:- ',secret_key)
# source_file_path ="D:/Cogent_Audio_Repo/"
# destination_folder = "D:/Cogent_AI_Audio_Repo/" 
# print('source_file_path path:- ',source_file_path)
# print('destination_folder path:- ',destination_folder)
#    # run the model from here
# build_transcribe_model(source_file_path, destination_folder)
if __name__ == '__main__':
     try:
      #   destination_folder =  os.getenv('destination_folder')
      #   source_file_path = os.getenv('source_file_path')
        source_file_path ="D:/Cogent_Audio_Repo/"
        destination_folder = "D:/Cogent_AI_Audio_Repo/" 
        build_transcribe_model(str(source_file_path), str(destination_folder))
     except Exception as e:   
        print(f'caught {type(e)}: e',e)
