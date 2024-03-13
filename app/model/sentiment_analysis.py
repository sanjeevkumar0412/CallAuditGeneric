from app.services.logger import Logger
import os,json
# os.environ["OPENAI_API_KEY"] = ""
from db_layer.models import AudioTranscribe,AudioTranscribeTracker,SentimentAnalysis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.engine.reflection import Inspector

dns = f'mssql+pyodbc://FLM-VM-COGAIDEV/AudioTrans?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(dns)
Session = sessionmaker(bind=engine)

session = Session()
from openai import OpenAI
client = OpenAI(
    # api_key=os.environ.get("OPENAI_API_KEY_NEW"),
    api_key=os.environ["OPENAI_API_KEY"],
)
class SentimentAnalysisCreation:
    # _instance = None

    def __init__(self, path):
        self.path = path
        self.logger = Logger()
    #
    # @classmethod
    # def get_instance(cls):
    #     if cls._instance is None:
    #         cls._instance = cls.__new__(cls)
    #     return cls._instance

    def get_sentiment(self,text):
        prompt = f"The following text expresses a sentiment: '{text}' The sentiment of this text is:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": ""}
            ],
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        # sentiment = response['choices'][0]['message']['content'].strip()
        sentiment = response.choices[0].message.content.strip()

        if "positive" in sentiment.lower():
            score = 1
        elif "negative" in sentiment.lower():
            score = -1
        else:
            score = 0
        data ={'sentiment':sentiment,'score':score}
        return data

    def transcribe_data_from_database(self,transcribe_data):
        #Databse Query here
        # table_name = 'AudioRecord'
        # column_value = 'filename'
        # with open(self.path, 'r') as file:# Read text data from the file
        #     texts = file.readlines()
        #     print(texts)
        print("Get data from another table >>>>>>>",len(transcribe_data))
        print("Get data Client name from another table >>>>>>>",transcribe_data.get("TranscribeMergeText"))
        transcribe_audio_data=transcribe_data.get("TranscribeMergeText")
        clientId=transcribe_data.get("ClientId")
        transcribId=transcribe_data.get("TranscribeId")
        clientId=transcribe_data.get("ClientId")

        exit()
        sentimentText = [{"text": text.strip(), "sentiment": self.get_sentiment(text.strip())['sentiment'],
                    "score": self.get_sentiment(text.strip())['score']} for text in transcribe_audio_data]
        # Column Name Id,ClientId,transcriptId,SentimentScore SentimentText,AnalysisDate,Created,Modified,IsActive,IsDeleted,SentimentStatus
        # column_input=("ClientId":)
        # SentimentAnalysis.add


        return sentimentText


    def get_data_from_transcribe_tracker_table(self, audio_id):
        try:

            audio_dictionary={}
            transcribe_text=[]

            check_audio_id_exits = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.AudioId == audio_id).first()
            print("check_audio_id_exits",check_audio_id_exits)
            if check_audio_id_exits:
                audio_id_query=session.query(AudioTranscribeTracker.AudioId).filter(AudioTranscribeTracker.AudioId==audio_id,AudioTranscribeTracker.ChunkStatus=='Completed')
                query_audio_id_results = audio_id_query.all()
                if query_audio_id_results !=[]:
                    query = session.query(AudioTranscribeTracker.ClientId,AudioTranscribeTracker.AudioId,AudioTranscribeTracker.ChunkFilePath,AudioTranscribeTracker.ChunkSequence, AudioTranscribeTracker.ChunkText).filter(
                        AudioTranscribeTracker.AudioId == audio_id)
                    results = query.all()
                    for row in results:
                        print("row outpupt",row.ClientId)
                        # print(">>>>>>>ChunkText",row["ChunkText"])
                        transcribe_text.append(row.ChunkText)
                        audio_dictionary.update({"ClientId":row.ClientId,"TranscribeId":row.AudioId,"ChunkSequence":row.ChunkSequence,"TranscribeMergeText":transcribe_text})
                        # print("chunk value >>>",audio_dictionary)
                        # print("transcribe_text",transcribe_text)
                else:
                    self.logger.info(f":Transcribe Job Status is pending")
            else:
                self.logger.info(f":Record not found {audio_id}")
            self.transcribe_data_from_database(audio_dictionary)
            # print("New Trans result from DB>>>",trans_result)
            # return transcribe_text

            # print("transcribe_text >>>>>>>",transcribe_text)
            print("dic>>>>>>>",audio_dictionary)
            return audio_dictionary
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            print(e)
        finally:
            pass
            # result.close()

if __name__ == "__main__":
    path="D:/Cogent-AI/app/chunk_6.txt"

    # Single Input Entry

    # input_text = input("Please enter input for Sentiment Analysis:")
    sentiment_instance=SentimentAnalysisCreation(path)
    # sentiment = sentiment_instance.get_sentiment(input_text)
    # print("Single Sentiment",sentiment)

    # For FIle or DB
    audio_id=38


    # audio_id_query = session.query(AudioTranscribeTracker.AudioId).filter(AudioTranscribeTracker.AudioId==audio_id,AudioTranscribeTracker.ChunkStatus == 'Completed')
    # query_results = audio_id_query.all()

    re=sentiment_instance.get_data_from_transcribe_tracker_table(audio_id)
    # print(">>>>>>>>>>>>audio_id_query query_results>>>>>>>>",re)
    # analyzer = SentimentAnalysisCreation(path)
    # sentiment_results = analyzer.transcribe_data_from_database()
    # sentiment_list_data= json.dumps(sentiment_results, indent=2)
    # print("Result>>>>>>",sentiment_list_data)