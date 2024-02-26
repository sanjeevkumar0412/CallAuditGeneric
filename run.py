import os
from dotenv import load_dotenv
from app.model.start_transcribe import StartTranscribe
from loguru import logger

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
        transcribe_model = StartTranscribe()
      #   destination_folder =  os.getenv('destination_folder')
      #   source_file_path = os.getenv('source_file_path')
        source_file_path ="D:/Cogent_Audio_Repo/"
        destination_folder = "D:/Cogent_AI_Audio_Repo/"
        is_source_path_exist = os.path.exists(source_file_path)
        is_destination_path_exist = os.path.exists(destination_folder) 
        if is_source_path_exist and is_destination_path_exist:
         transcribe_model.start_transcribe_process(str(source_file_path), str(destination_folder),'Small') #Premium, Normal, Small
        else:
          logger.error('folder path does not exist')
     except Exception as e:   
        print(f'caught {type(e)}: e',e)
