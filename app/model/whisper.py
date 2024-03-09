import whisper 
import time
from app.utilities.utility import GlobalUtility
from app.services.logger import Logger
class WhisperModel: 
    _instance = None

    def __init__(self):      
        self.global_utility =  GlobalUtility()
        self.logger = Logger()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def whisper_transcribe_audio(self,file_path,model_name ="tiny"):
        try:
            model = whisper.load_model(model_name)
            result = model.transcribe(file_path)
            return result
        except Exception as e:                       
                        print(f"Error transcribing : {e}")
                        self.retries_model(file_path,model_name) 
           
    def whisper_transcribe_large_audio(self,file_path,model_name ="tiny"):       
            model = whisper.load_model(model_name)
            try:               
                    result = model.transcribe(file_path)                    
                    return  result                        
            except Exception as e:                       
                        print(f"Error transcribing : {e}")
                        self.retries_model(file_path,model_name)                   

    def retries_model(self,failed_file,model_name):           
            retries =3
            model = whisper.load_model(model_name)
            for attempt in range(retries):
                try:
                    print('fialed file process start : ',failed_file)
                    time.sleep(2**attempt)
                    result = model.transcribe(failed_file)
                    return result                   
                    # break  
                except Exception as e:
                    print(f"Failed to transcribe {failed_file} even after {attempt+1} attempt(s): {e}")                    
             