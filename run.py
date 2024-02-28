import os
from dotenv import load_dotenv
from app.model.start_transcribe import StartTranscribe
from loguru import logger

load_dotenv()


def main():
    # Your main program logic goes here
    try:
        transcribe_model = StartTranscribe()      
      #   source_file_path ="D:/Cogent_Audio_Repo/"
      #   destination_folder = "D:/Cogent_AI_Audio_Repo/"
      #   is_source_path_exist = os.path.exists(source_file_path)
      #   is_destination_path_exist = os.path.exists(destination_folder) 
      #   if is_source_path_exist and is_destination_path_exist:
        transcribe_model.start_transcribe_process() #Premium, Normal, Small
      #   else:
      #     logger.error('folder path does not exist')
    except Exception as e:   
        print(f'caught {type(e)}: e',e)

if __name__ == '__main__':
     main()
