from app.services.logger import Logger
import os
import json
from app.utilities.utility import GlobalUtility
from datetime import datetime
from db_layer.models import AudioTranscribeTracker,SentimentAnalysis,AudioTranscribe,JobStatus
from sqlalchemy.exc import IntegrityError
from app import prompt_check_list
os.environ["OPENAI_API_KEY"] = ""

from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # api_key=os.environ["OPENAI_API_KEY"],
)
class SentimentAnalysisCreation:

    def __init__(self):
        self.logger = Logger()
        self.global_utility = GlobalUtility()

    def get_sentiment(self,text):
        prompt = f"{prompt_check_list.prompt_text}Please check the conversation and provide the aggregate Sentiment and Score vallue{text}"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # model="gpt-4",
            messages=[
                # {"role": "system", "content": prompt},
                {"role": "user", "content": prompt}
            ],

            max_tokens=500,
            n=1,
            presence_penalty=0,
            stop=None,
            temperature=0.8
            # stop=["\n"]
        )
        # sentiment = response['choices'][0]['message']['content'].strip()
        sentiment = response.choices[0].message.content
        aggregate_sentiment= json.loads(sentiment)["aggregate_sentiment"]
        aggregate_score= json.loads(sentiment)["aggregate_score"]
        if "positive" in sentiment.lower():
            score = 1
        elif "negative" in sentiment.lower():
            score = -1
        else:
            score = 0

        data ={'aggregate_sentiment':aggregate_sentiment,'aggregate_score':aggregate_score,'score':score}
        return data

    def dump_data_into_sentiment_database(self, server_name, database_name, client_id,transcribe_data):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)
        try:
            transcribe_audio_data=transcribe_data.get("TranscribeMergeText")
            clientid=transcribe_data.get("ClientId")
            current_file=transcribe_data.get("filename")
            transcribid=transcribe_data.get("TranscribeId")
            created_sentiment_date = datetime.utcnow()
            # sentiment_status= self.global_utility.get_status_by_key_name(self.global_utility.get_job_status_data(),'PreProcessing')
            analysis_sentiment_date = datetime.utcnow()
            file_entry_check = session.query(SentimentAnalysis).filter_by(AudioFileName=current_file).all()

            if file_entry_check is None:
                dump_data_into_table = SentimentAnalysis(ClientId=clientid,
                                                      AnalysisDateTime=analysis_sentiment_date, SentimentStatus=2,
                                                      AudioFileName=current_file,Created=created_sentiment_date, \

                                                      )
                session.add(dump_data_into_table)
                session.commit()
            else:
                # sentiment_output_data = [{"text": text.strip(), "sentiment": self.get_sentiment(text.strip())['sentiment'],
                #                           "score": self.get_sentiment(text.strip())['score']} for text in transcribe_audio_data]

                sentiment_call_data=[self.get_sentiment(text) for text in transcribe_audio_data]
                # sentiment_json_load=json.loads(sentiment_call_data[0]['sentiment'])
                sentiment_output_data=sentiment_call_data[0]

                if len(sentiment_call_data) > 0:

                    update_sentiment_record = session.query(SentimentAnalysis).filter(SentimentAnalysis.AudioFileName == current_file).first()
                    modified_sentiment_date = datetime.utcnow()

                    if update_sentiment_record:
                        update_sentiment_record.SentimentScore=sentiment_output_data['aggregate_score']
                        update_sentiment_record.SentimentText=transcribe_audio_data[0]
                        update_sentiment_record.SentimentStatus=3
                        update_sentiment_record.Modified=modified_sentiment_date
                        update_sentiment_record.Sentiment=sentiment_output_data['aggregate_sentiment']
                        session.commit()
            result={"status":"200","message":"Sentiment Record successfully recorded !"}
            return result
        except IntegrityError as e:
            session.rollback()
            print("Error:", e)
        finally:
            session.close()

    def get_data_from_transcribe_table(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)
        try:
            audio_dictionary = {}
            transcribe_text = []
            check_audio_id_exits = session.query(AudioTranscribe).filter(
                AudioTranscribe.AudioFileName == audio_file).first()
            if len(check_audio_id_exits) > 0:
                audio_id_query = session.query(AudioTranscribe.Id).filter(
                    AudioTranscribe.AudioFileName == audio_file)
                    # AudioTranscribeTracker.ChunkStatus == 'Completed')
                query_audio_id_results = audio_id_query.all()
                if len(query_audio_id_results) > 0:
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
        finally:
            session.close()



    def get_transcribe_data_for_sentiment(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)
        try:
            audio_dictionary = {}
            transcribe_text = []
            check_audio_file_exits = session.query(AudioTranscribe).filter(
                AudioTranscribe.AudioFileName == audio_file).all()
            # print("check_audio_id_exits", check_audio_file_exits)
            if len(check_audio_file_exits) > 0:
                audio_id_query = session.query(AudioTranscribe.Id).filter(
                    AudioTranscribe.AudioFileName == audio_file)
                    # AudioTranscribeTracker.ChunkStatus == 'Completed')
                query_audio_id_results = audio_id_query.all()
                if len(query_audio_id_results) > 0:
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
                                                 "TranscribeMergeText": transcribe_text,"filename":audio_file})
                else:
                    self.logger.info(f":Transcribe Job Status is pending")
            else:
                self.logger.info(f":Record not found {audio_file}")
            # self.get_sentiment1(transcribe_text)
            self.dump_data_into_sentiment_database(server_name, database_name, client_id, audio_dictionary)

            result = {"transcribe_data": transcribe_text,"status": 200}
            return result
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            print(e)
            # result.close()
        finally:
            session.close()

    def get_sentiment_data_from_table(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)

        try:
            sentiment_dic={}
            data = session.query(SentimentAnalysis).filter_by(AudioFileName=audio_file).all()
            sentiment_dic.update({"Id":data[0].Id,"ClientId":data[0].ClientId,"AnalysisDateTime":data[0].AnalysisDateTime,"AudioFileName":data[0].AudioFileName,"Created":data[0].Created,"SentimentScore":data[0].SentimentScore,"SentimentStatus":data[0].SentimentStatus,"Modified":data[0].Modified,"Sentiment":data[0].Sentiment})
            result = {"sentimentdata": sentiment_dic,"status": 200}
            return result
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            print(e)
        finally:
            session.close()

if __name__ == "__main__":

    # input_text = input("Please enter input for Sentiment Analysis:")
    sentiment_instance=SentimentAnalysisCreation()
    # sentiment = sentiment_instance.get_sentiment(input_text)
    # print("Single Sentiment",sentiment)

    # For FIle or DB
    audio_path='CallRecording111234.mp3'
    server_name = 'FLM-VM-COGAIDEV'
    database_name = 'AudioTrans'
    # re=sentiment_instance.get_data_from_transcribe_table(audio_path)
    # re=sentiment_instance.get_sentiment_data_from_table(audio_path)
    re=sentiment_instance.get_transcribe_data_for_sentiment(server_name,database_name,1,audio_path)
    # print("By File Name>>",re)


    # print(">>>>>>>>>>>>audio_id_query query_results>>>>>>>>",re)
    # analyzer = SentimentAnalysisCreation(path)
    # sentiment_results = analyzer.dump_data_into_sentiment_database()
    # sentiment_list_data= json.dumps(sentiment_results, indent=2)
    # print("Result>>>>>>",sentiment_list_data)


