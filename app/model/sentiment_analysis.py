from app.services.logger import Logger
import os
from datetime import datetime
from db_layer.models import AudioTranscribeTracker,SentimentAnalysis,AudioTranscribe
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
os.environ["OPENAI_API_KEY"] = ""

dns = f'mssql+pyodbc://FLM-VM-COGAIDEV/AudioTrans?driver=ODBC+Driver+17+for+SQL+Server'
engine = create_engine(dns)
Session = sessionmaker(bind=engine)

session = Session()
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # api_key=os.environ["OPENAI_API_KEY"],
)
class SentimentAnalysisCreation:

    def __init__(self):
        self.logger = Logger()

    def get_sentiment(self,text):

        prompt = f" Your role is Business Analyst who reads the transcription of discussion between Deator and Recovery agent of any recovery comp   its sentiment? We're interested in understanding the overall mood or feeling conveyed in the recording. Your insights will help us gain a better understanding of the emotional tone of the content:'{text}' The sentiment of this text is:"
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

    def dump_data_into_sentiment_database(self,transcribe_data):

        try:
            transcribe_audio_data=transcribe_data.get("TranscribeMergeText")
            clientid=transcribe_data.get("ClientId")
            transcribid=transcribe_data.get("TranscribeId")
            created_sentiment_date = datetime.utcnow()

            analysis_sentiment_date = datetime.utcnow()

            sentiment_output_data = [{"text": text.strip(), "sentiment": self.get_sentiment(text.strip())['sentiment'],
                                      "score": self.get_sentiment(text.strip())['score']} for text in transcribe_audio_data]

            modified_sentiment_date = datetime.utcnow()

            sentiment_column_data = SentimentAnalysis(ClientId=clientid, SentimentScore=sentiment_output_data[0]['score'],SentimentText=sentiment_output_data[0]['text'], \
                                                     AnalysisDateTime=analysis_sentiment_date,SentimentStatus=2,Created=created_sentiment_date, \
                                                     Modified=modified_sentiment_date,Sentiment=sentiment_output_data[0]['sentiment']
                                                     )
            session.add(sentiment_column_data)
            session.commit()

            # sentiment_id_current = session.query(SentimentAnalysis.Id).filter(SentimentAnalysis.Id == transcribid)
            # sentiment_id_res=sentiment_id_current.first()
            # print("sentiment_id_currentsentiment_id_current>>>",sentiment_id_current)
            # print("sentiment_id_res>>>",sentiment_id_res)
            # sentiment_status_update = session.query(SentimentAnalysis).filter(SentimentAnalysis.Id == transcribid,SentimentAnalysis.Id==sentiment_id_res,SentimentAnalysis.SentimentStatus=="Inprogress").first()
            #
            # if sentiment_status_update:
            #     sentiment_status_update.SentimentStatus="Completed"
            #     # for sentiment_status in sentiment_status_update:
            #     #     sentiment_status.SentimentStatus="Completed"
            #     session.commit()
            #     print("Sentiment status successfully updated !")
            # else:
            #     print("Error while updating sentiment status !")
            #
            return sentiment_column_data

        except IntegrityError as e:
            session.rollback()
            print("Error:", e)

    def get_data_from_transcribe_table(self, audio_file):
        try:

            audio_dictionary = {}
            transcribe_text = []

            check_audio_id_exits = session.query(AudioTranscribe).filter(
                AudioTranscribe.AudioFileName == audio_file).first()
            print("check_audio_id_exits", check_audio_id_exits)
            if check_audio_id_exits:
                audio_id_query = session.query(AudioTranscribe.Id).filter(
                    AudioTranscribe.AudioFileName == audio_file)
                    # AudioTranscribeTracker.ChunkStatus == 'Completed')
                query_audio_id_results = audio_id_query.all()
                if query_audio_id_results != []:
                    query = session.query(AudioTranscribeTracker.ClientId, AudioTranscribeTracker.AudioId,
                                          AudioTranscribeTracker.ChunkFilePath,
                                          AudioTranscribeTracker.ChunkSequence,
                                          AudioTranscribeTracker.ChunkText).filter(
                        AudioTranscribeTracker.AudioId == audio_id_query)
                    results = query.all()
                    for row in results:
                        print("row outpupt", row.ClientId)
                        transcribe_text.append(row.ChunkText)
                        audio_dictionary.update({"ClientId": row.ClientId, "TranscribeId": row.AudioId,
                                                 "ChunkSequence": row.ChunkSequence,
                                                 "TranscribeMergeText": transcribe_text})
                else:
                    self.logger.info(f":Transcribe Job Status is pending")
            else:
                self.logger.info(f":Record not found {audio_file}")
            result = {"transcribe_data": transcribe_text, "status": 200}
            return result
        except Exception as e:
            self.logger.error(f": Error {e}",e)
            print(e)
            # result.close()



    def get_transcribe_data_for_sentiment(self, audio_file):
        try:

            audio_dictionary = {}
            transcribe_text = []

            check_audio_id_exits = session.query(AudioTranscribe).filter(
                AudioTranscribe.AudioFileName == audio_file).first()
            print("check_audio_id_exits", check_audio_id_exits)
            if check_audio_id_exits:
                audio_id_query = session.query(AudioTranscribe.Id).filter(
                    AudioTranscribe.AudioFileName == audio_file)
                    # AudioTranscribeTracker.ChunkStatus == 'Completed')
                query_audio_id_results = audio_id_query.all()
                if query_audio_id_results != []:
                    query = session.query(AudioTranscribeTracker.ClientId, AudioTranscribeTracker.AudioId,
                                          AudioTranscribeTracker.ChunkFilePath,
                                          AudioTranscribeTracker.ChunkSequence,
                                          AudioTranscribeTracker.ChunkText).filter(
                        AudioTranscribeTracker.AudioId == audio_id_query)
                    results = query.all()
                    for row in results:
                        print("row outpupt", row.ClientId)
                        transcribe_text.append(row.ChunkText)
                        audio_dictionary.update({"ClientId": row.ClientId, "TranscribeId": row.AudioId,
                                                 "ChunkSequence": row.ChunkSequence,
                                                 "TranscribeMergeText": transcribe_text})
                        # print("chunk value >>>",audio_dictionary)
                        # print("transcribe_text",transcribe_text)
                else:
                    self.logger.info(f":Transcribe Job Status is pending")
            else:
                self.logger.info(f":Record not found {audio_file}")
            self.dump_data_into_sentiment_database(audio_dictionary)
            result = {"transcribe_data": transcribe_text, "status": 200}
            return result
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            print(e)
            # result.close()

if __name__ == "__main__":

    # input_text = input("Please enter input for Sentiment Analysis:")
    sentiment_instance=SentimentAnalysisCreation()
    # sentiment = sentiment_instance.get_sentiment(input_text)
    # print("Single Sentiment",sentiment)

    # For FIle or DB
    audio_path='CallRecording111234.mp3'

    # re=sentiment_instance.get_data_from_transcribe_table(audio_path)
    re=sentiment_instance.get_transcribe_data_for_sentiment(audio_path)
    print("By File Name>>",re)


    # print(">>>>>>>>>>>>audio_id_query query_results>>>>>>>>",re)
    # analyzer = SentimentAnalysisCreation(path)
    # sentiment_results = analyzer.dump_data_into_sentiment_database()
    # sentiment_list_data= json.dumps(sentiment_results, indent=2)
    # print("Result>>>>>>",sentiment_list_data)