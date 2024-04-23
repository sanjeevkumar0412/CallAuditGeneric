from app.services.logger import Logger
import os
import json
from app.utilities.utility import GlobalUtility
from datetime import datetime
from db_layer.models import AudioTranscribeTracker,SentimentAnalysis,AudioTranscribe,ProhibitedKeyword,JobStatus
from sqlalchemy.exc import IntegrityError
from app.configs.error_code_enum import *
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

    def get_sentiment(self,text,prompt_inject):
        try:
            status = 'success'
            prompt = f'{prompt_check_list.sentiment_prompt} {prompt_inject}.The conversation text will be available between two @@@. For giving responses follows these JSON key value only in 1) Summary 2).Topics,3)FoulLanguage 4)ActionItems 5)ActionOwners 6)Score 7)AggregateSentiment 8)Compliance Score and 9)Good bye reminder message and date also.for JSON key Topics you will return subset in the format as follows "Topic": "<Topic Name>","Sentiment": "<Positive/Negative/Neutral>","FoulLanguage": "<Yes/NO>" ,"ActionItems": ["<List of Action items for the topic>"],"ActionOwners": ["<Owner of actions>"],"Score": "<Sentiment Score out of 10>".Be careful about future and past date and time predictions as they are associate about future actions items. For example if reminder is for after a month then you need to generate required date as SUM of Date Mentioned in transcription Plus 1 month and if it is for 1 week then it would be date discussed in transcription Plus 1 week. Transcribe text starts as follows @@@ {text}. @@@.Make sure that action item will not contain any blank values. Blank value will only be considered in exceptional cases.'
            # sentiment = response['choices'][0]['message']['content'].strip()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                # model="gpt-4",
                messages=[
                    {"role": "system", "content": prompt},
                    # {"role": "user", "content": prompt}
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
            self.logger.error(f" Sentiment Error in method get_sentiment",str(e))
            return status, set_json_format([str(e)], e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))

    def dump_data_into_sentiment_database(self, server_name, database_name, client_id,transcribe_data):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string)
            try:
                prompt_inject= self.get_prohibited_data_from_table(server_name, database_name, client_id)
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
                    status, sentiment_call_data = self.get_sentiment(transcribe_merged_string, prompt_inject[0])
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
                        result=set_json_format([], SUCCESS, True, f"Sentiment Record successfully recorded for the file {current_file}")
                        return result,SUCCESS
                    else:
                        return sentiment_call_data,RESOURCE_NOT_FOUND
                else:
                    #Update Logic
                    status, sentiment_call_data = self.get_sentiment(transcribe_merged_string, prompt_inject[0])
                    if status == "success":
                        update_column_dic = {SentimentAnalysis.Sentiment:str(sentiment_call_data['average_sentiment']),
                                             SentimentAnalysis.Modified:modified_sentiment_date,
                                             SentimentAnalysis.SentimentScore:str(sentiment_call_data['sentiment_score']),
                                             SentimentAnalysis.ActionItems:str(sentiment_call_data['action_items']),
                                             SentimentAnalysis.Topics:str(sentiment_call_data['topics']),SentimentAnalysis.Owners:str(sentiment_call_data['owners']),
                                             SentimentAnalysis.FoulLanguage:str(sentiment_call_data['foul_language'])
                                             }
                        session.query(SentimentAnalysis).filter_by(AudioFileName=current_file).update(update_column_dic)
                        session.commit()
                        result = {"status": SUCCESS,"message": f"Sentiment Record has been updated successfully for this {current_file}"}
                        self.logger.info(f"Sentiment Record has been updated successfully for this {current_file}")
                        return result,SUCCESS
                    else:
                        self.logger.error(f"Error occured while updating updating Sentiment record {sentiment_call_data}", RESOURCE_NOT_FOUND)
                        return sentiment_call_data, INTERNAL_SERVER_ERROR
            except IntegrityError as e:
                self.logger.error(f"Found error in dump_data_into_sentiment_database or get_sentiment",str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Sentiment Error in method get_sentiment", str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e)),RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in dump_data_into_sentiment_database or get_sentiment", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Sentiment Error in method get_sentiment", str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
            finally:
                session.close()

        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def get_data_from_transcribe_table(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string)
            logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
            # session = self.global_utility.get_database_session(connection_string)
            try:
                audio_dictionary = {}
                transcribe_text = []
                trans_dic={}
                check_audio_id_exits = session.query(AudioTranscribe).filter(
                    AudioTranscribe.AudioFileName == audio_file).all()

                if len(check_audio_id_exits) > 0:
                    audio_id_query = session.query(AudioTranscribe.Id).filter(
                        AudioTranscribe.AudioFileName == audio_file)
                    query_audio_id_results = audio_id_query.all()
                    check_chunk_exist = session.query(AudioTranscribeTracker.ChunkText).filter(
                        AudioTranscribeTracker.AudioId == query_audio_id_results[0][0])
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
                                                     "TranscribeMergeText": transcribe_text})
                    else:
                        self.logger.info(f":ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table")
                        data = {"status":RESOURCE_NOT_FOUND,"message": f"ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table"}
                        return data,RESOURCE_NOT_FOUND
                else:
                    self.logger.info(f":Record not found {audio_file} in AudioTranscribe Table")
                    data = {"message": f"Record not found {audio_file} in AudioTranscribe Table","status":RESOURCE_NOT_FOUND}
                    return data,RESOURCE_NOT_FOUND
                result = {"message": ''.join(transcribe_text), "status": SUCCESS}
                return result,SUCCESS
            except Exception as e:
                self.logger.error(f": get_data_from_transcribe_table {e}",e)
                error_array = []
                error_array.append(str(e))
                self.logger.error('Error in Method get_data_from_transcribe_table ', str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
                session.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR



    def get_transcribe_data_for_sentiment(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string)
            logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
            # session = self.global_utility.get_database_session(connection_string)
            try:
                audio_dictionary = {}
                transcribe_text = []
                check_audio_file_exits = session.query(AudioTranscribe).filter(
                    AudioTranscribe.AudioFileName == audio_file).all()
                if len(check_audio_file_exits) > 0:
                    audio_id_query = session.query(AudioTranscribe.Id).filter(
                        AudioTranscribe.AudioFileName == audio_file)
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
                        data= {"status":RESOURCE_NOT_FOUND,"message":f":ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table"}
                        return data,RESOURCE_NOT_FOUND
                else:
                    self.logger.info(f":Record not found {audio_file}")
                    data= {"message":f":Record not found {audio_file} in AudioTranscribe Table"}
                    return data,RESOURCE_NOT_FOUND
                return self.dump_data_into_sentiment_database(server_name, database_name, client_id, audio_dictionary)
            except Exception as e:
                # self.logger.error(f": Error {e}",e)
                error_array = []
                error_array.append(str(e))
                self.logger.error('Error in Method get_connection_string ', str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
                # result.close()
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
                session.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def get_sentiment_data_from_table(self, server_name, database_name, client_id,audio_file):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string)
            logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
            # session = self.global_utility.get_database_session(connection_string)
            check_audio_file_exits = session.query(SentimentAnalysis).filter(
                SentimentAnalysis.AudioFileName == audio_file).all()

            try:
                if len(check_audio_file_exits) > 0:
                    sentiment_dic={}
                    data = session.query(SentimentAnalysis).filter_by(AudioFileName=audio_file).all()
                    sentiment_dic.update({"Id":data[0].Id,"ClientId":data[0].ClientId,
                                          "AnalysisDateTime":data[0].AnalysisDateTime,"AudioFileName":data[0].AudioFileName,
                                          "Created":data[0].Created,"SummaryReport":data[0].Summary,"Topics":data[0].Topics,
                                          "FoulLanguage":data[0].FoulLanguage,"ActionItems":data[0].ActionItems,
                                          "Owners":data[0].Owners,"SentimentScore":data[0].SentimentScore,
                                          "SentimentStatus":data[0].SentimentStatus,
                                          "Modified":data[0].Modified,"Sentiment":data[0].Sentiment})
                    # result = {"sentimentdata": sentiment_dic}
                    result = sentiment_dic
                    return result,SUCCESS
                else:
                    data = {"message": f"Record not found {audio_file} in AudioTranscribe Table"}
                    return data,RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in get_sentiment_data_from_table", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Fetch record from Sentiment table Error in method get_sentiment_data_from_table", str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
                # self.logger.error(f": Error {e}",e)
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
                session.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def get_prohibited_data_from_table(self, server_name, database_name, client_id):
        connection_string = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string)
            logger_handler = self.logger.log_entry_into_sql_table(session, client_id, False)
            check_data_exist = session.query(ProhibitedKeyword).all()

            try:
                if len(check_data_exist) > 0:
                    prohibited_data=[]
                    data = session.query(ProhibitedKeyword).filter_by(ClientID=client_id).all()
                    for key_data in data:
                        prohibited_data.append(key_data.Keywords)

                    result=','.join(prohibited_data)

                    return result,SUCCESS
                else:
                    data = {"message": f"Record not found {client_id} in ProhibitedKeyword Table"}
                    return data,RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in ProhibitedKeyword", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Fetch record from Sentiment table Error in method get_sentiment_data_from_table", str(e))
                return set_json_format(error_array, RESOURCE_NOT_FOUND, False, str(e))
                # self.logger.error(f": Error {e}",e)
            finally:
                self.logger.log_entry_into_sql_table(session, client_id, True,logger_handler)
                session.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def calculate_max_tokens(self, text, token_size=1):

        words = text.split()
        tokens_count = len(words) * token_size
        return tokens_count