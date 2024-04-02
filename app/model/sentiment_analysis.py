from app.services.logger import Logger
import os
import json
from app.utilities.utility import GlobalUtility
from datetime import datetime
from db_layer.models import AudioTranscribeTracker,SentimentAnalysis,AudioTranscribe,JobStatus
from sqlalchemy.exc import IntegrityError
from app import prompt_check_list
os.environ["OPENAI_API_KEY"] = prompt_check_list.open_ai_key
from flask_end_points_service import set_json_format
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # api_key=os.environ["OPENAI_API_KEY"],
)
class SentimentAnalysisCreation:

    def __init__(self):
        self.logger = Logger()
        self.global_utility = GlobalUtility()

    def get_sentiment(self,text,calulated_max_tokens):
        try:
            status = 'success'
            prompt = f'{prompt_check_list.prompt1}{text} @@@ For giving responses follows these JSON key value only in 1) Summary 2).Topics,3)FoulLanguage 4)ActionItems 5)ActionOwners 6)Score 7)AggregateSentiment. for JSON key Topics you will return subset in the format as follows "Topic": "<Topic Name>","Sentiment": "<Positive/Negative/Neutral>","FoulLanguage": "<Yes/NO>" ,"ActionItems": ["<List of Action items for the topic>"],"ActionOwners": ["<Owner of actions>"],"Score": "<Sentiment Score out of 10>"'
            # sentiment = response['choices'][0]['message']['content'].strip()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                # model="gpt-4",
                messages=[
                    # {"role": "system", "content": prompt},
                    {"role": "user", "content": prompt}
                ],

                max_tokens=1500,
                n=1,
                presence_penalty=0.8,
                temperature=0.2,
                top_p=1.0,
                stop=None
                # stop=["\n"]
            )
            sentiment = response.choices[0].message.content
            results = json.loads(sentiment)
            if 'Summary' in results:
                summary_report = results['Summary']
            else:
                summary_report = 'key not Summary not found'

            if 'Topics' in results:
                topics = results['Topics']
            else:
                topics = 'key Topics not found'
            if 'FoulLanguage' in results:
                foul_language = results['FoulLanguage']
            else:
                foul_language = 'key Foul Language not found'

            if 'ActionItems' in results:
                action_items = results['ActionItems']
            else:
                action_items = 'key Action Items not found'

            if 'ActionOwners' in results:
                owners = results['ActionOwners']
            else:
                owners = 'key Owners not found'
            if 'Score' in results:
                sentiment_score = results['Score']
            else:
                sentiment_score = 'key Score not found'

            if 'AggregateSentiment' in results:
                average_sentiment = results['AggregateSentiment']
            else:
                average_sentiment = 'key Aggregate Sentiment not found'

            data = {'summary_report': summary_report, 'topics': topics, 'foul_language': foul_language,
                    'action_items': action_items, 'owners': owners, 'sentiment_score': sentiment_score,
                    'average_sentiment': average_sentiment}
            return status, data
        except Exception as e:
            status = 'failure'
            error_array = []
            error_array.append(str(e))
            self.logger.error(f" Sentiment Error in method get_sentiment",str(e))
            return status, set_json_format(error_array, 500, False, str(e))

    def dump_data_into_sentiment_database(self, server_name, database_name, client_id,transcribe_data):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)
        try:
            transcribe_audio_data=transcribe_data.get("TranscribeMergeText")
            transcribe_merged_string = '.'.join(transcribe_audio_data)
            clientid=transcribe_data.get("ClientId")
            current_file=transcribe_data.get("filename")
            created_sentiment_date = datetime.utcnow()
            analysis_sentiment_date = datetime.utcnow()
            modified_sentiment_date = datetime.utcnow()
            calulated_max_tokens = self.calculate_max_tokens(transcribe_merged_string, token_size=1)
            file_entry_check = session.query(SentimentAnalysis).filter_by(AudioFileName=current_file).all()
            if len(file_entry_check) == 0:
                status, sentiment_call_data = self.get_sentiment(transcribe_merged_string, calulated_max_tokens)
                if status == 'success':
                    dump_data_into_table = SentimentAnalysis(ClientId=clientid,
                                                          AnalysisDateTime=analysis_sentiment_date, SentimentStatus=21,
                                                          AudioFileName=current_file,Created=created_sentiment_date,
                                                             SentimentScore=str(sentiment_call_data['sentiment_score']),
                                                             SentimentText=transcribe_merged_string,Modified=modified_sentiment_date,
                                                             Sentiment=str(sentiment_call_data['average_sentiment']),Summary=str(sentiment_call_data['summary_report']),
                                                             Topics=str(sentiment_call_data['topics']),FoulLanguage=str(sentiment_call_data['foul_language']),
                                                             ActionItems=str(sentiment_call_data['action_items']),Owners=str(sentiment_call_data['owners']))
                    session.add(dump_data_into_table)
                    session.commit()
                    result=set_json_format([], 200, True, f"Sentiment Record successfully recorded for the file {current_file}")
                    return result
                else:
                    return sentiment_call_data
            else:
                result={"status":"200","message":f"Sentiment Record already available for this {current_file}"}
                return result

        except IntegrityError as e:
            self.logger.error(f"Found error in dump_data_into_sentiment_database or get_sentiment",str(e))
            error_array = []
            error_array.append(str(e))
            self.logger.error(f" Sentiment Error in method get_sentiment", str(e))
            return set_json_format(error_array, e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))
        except Exception as e:
            self.logger.error(f"Found error in dump_data_into_sentiment_database or get_sentiment", str(e))
            error_array = []
            error_array.append(str(e))
            self.logger.error(f" Sentiment Error in method get_sentiment", str(e))
            return set_json_format(error_array, e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))
        finally:
            session.close()

    def get_data_from_transcribe_table(self, server_name, database_name, client_id,audio_file):
        self.logger.log_entry_into_sql_table(server_name, database_name, client_id, False)
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)
        try:
            audio_dictionary = {}
            transcribe_text = []
            check_audio_id_exits = session.query(AudioTranscribe).filter(
                AudioTranscribe.AudioFileName == audio_file).all()
            if len(check_audio_id_exits) > 0:
                audio_id_query = session.query(AudioTranscribe.Id).filter(
                    AudioTranscribe.AudioFileName == audio_file)
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
            self.logger.log_entry_into_sql_table(server_name, database_name, client_id, True)
            session.close()



    def get_transcribe_data_for_sentiment(self, server_name, database_name, client_id,audio_file):
        self.logger.log_entry_into_sql_table(server_name, database_name, client_id, False)
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
                check_chunk_exist = session.query(AudioTranscribeTracker.ChunkText).filter(
                    AudioTranscribeTracker.AudioId == query_audio_id_results[0][0])
                # blank_emails = session.query(AudioTranscribeTracker).filter(AudioTranscribeTracker.ChunkText == '').all()
                chunk_results_check = check_chunk_exist.all()
                if len(query_audio_id_results) > 0 and chunk_results_check[0][0] !=None:
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
                    data= {"status":204,"message":f":ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table"}
                    return data
            else:
                self.logger.info(f":Record not found {audio_file}")
                data= {"status":404,"message":f":Record not found {audio_file} in AudioTranscribe Table"}
                return data
            return self.dump_data_into_sentiment_database(server_name, database_name, client_id, audio_dictionary)
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            error_array = []
            error_array.append(str(e))
            self.logger.error('Error in Method get_connection_string ', str(e))
            return set_json_format(error_array, 500, False, str(e))
            # result.close()
        finally:
            self.logger.log_entry_into_sql_table(server_name, database_name, client_id, True)
            session.close()

    def get_sentiment_data_from_table(self, server_name, database_name, client_id,audio_file):
        self.logger.log_entry_into_sql_table(server_name, database_name, client_id, False)
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        session = self.global_utility.get_database_session(connection_string)

        try:
            sentiment_dic={}
            data = session.query(SentimentAnalysis).filter_by(AudioFileName=audio_file).all()
            sentiment_dic.update({"Id":data[0].Id,"ClientId":data[0].ClientId,
                                  "AnalysisDateTime":data[0].AnalysisDateTime,"AudioFileName":data[0].AudioFileName,
                                  "Created":data[0].Created,"SummaryReport":data[0].Summary,"Topics":data[0].Topics,
                                  "FoulLanguage":data[0].FoulLanguage,"ActionItems":data[0].ActionItems,
                                  "Owners":data[0].Owners,"SentimentScore":data[0].SentimentScore,
                                  "SentimentStatus":data[0].SentimentStatus,
                                  "Modified":data[0].Modified,"Sentiment":data[0].Sentiment})
            result = {"sentimentdata": sentiment_dic,"status": 200}
            return result
        except Exception as e:
            # self.logger.error(f": Error {e}",e)
            print(e)
        finally:
            self.logger.log_entry_into_sql_table(server_name, database_name, client_id, True)
            session.close()

    def calculate_max_tokens(self, text, token_size=1):

        words = text.split()
        tokens_count = len(words) * token_size
        return tokens_count