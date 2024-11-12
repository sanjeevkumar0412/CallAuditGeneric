from app.services.logger import Logger
import os
import json
from app.utilities.utility import GlobalUtility
from datetime import datetime
from db_layer.models import AudioTranscribeTracker,SentimentAnalysis,AudioTranscribe,ProhibitedKeyword,JobStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_,desc
from app.configs.error_code_enum import *
bussiness_model = os.environ.get("bussiness_model")
if bussiness_model=="cogent":
    from app import prompt_check_list
    prompt_data = prompt_check_list
else:
    from app import genric_prompt
    prompt_data = genric_prompt

from app import prompt_check_list
os.environ["OPENAI_API_KEY"] = prompt_check_list.open_ai_key
# os.environ["OPENAI_API_KEY"] = genric_prompt.open_ai_key
from flask_end_points_service import set_json_format
from flask import request
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    # api_key=os.environ["OPENAI_API_KEY"],
)
from sqlalchemy import func
open_ai_model=os.environ.get("open_ai_model")

class SentimentAnalysisCreation:

    def __init__(self):
        self.logger = Logger()
        self.global_utility = GlobalUtility()

    def get_sentiment(self,text,prohibited_prompt_inject):
        try:
            status = 'success'
            prompt = "{} {} {} @@@ {}.@@@. {}".format(prompt_data.sentiment_prompt,prohibited_prompt_inject,prompt_data.sentiment_prompt_after_inject,text,prompt_data.prompt_for_data_key_never_blank)
            response = client.chat.completions.create(
                model=open_ai_model,
                messages=[
                    # {"role": "system", "content": prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                n=1,
                presence_penalty=0.8,
                temperature=0.2,
                top_p=0.8,
                stop=None
                # stop=["\n"]
                #OrgName
                #DebtorName
                #EmployeeName

            )
            sentiment = response.choices[0].message.content
            json_string_cleaned = sentiment.replace('```', '').replace('\n', '').replace('json', '')
            results = json.loads(json_string_cleaned)
            if 'Summary' in results:
                summary_report = results['Summary']
            else:
                summary_report = ''

            if 'Topics' in results:
                topics = results['Topics']
            else:
                topics = ''
            if 'FoulLanguage' in results:
                foul_language = results['FoulLanguage']
            else:
                foul_language = 'No'

            if 'ActionItems' in results:
                action_items = results['ActionItems']
            else:
                action_items = 'No ActionItems.'

            if 'ActionItemsOwners' in results:
                owners = results['ActionItemsOwners']
            else:
                owners = 'N/A'
            if 'Score' in results:
                sentiment_score = results['Score']
            else:
                sentiment_score = '0'

            if 'AggregateSentiment' in results:
                average_sentiment = results['AggregateSentiment']
            else:
                average_sentiment = 'Neutral'

            if 'Good bye reminder message' in results:
                reminder_message = results['Good bye reminder message']
            else:
                reminder_message = 'N/A'

            if 'OrganisationName' in results:
                org_name = results['OrganisationName']
            else:
                org_name = 'N/A'

            if 'EmployeeName' in results:
                emp_name = results['EmployeeName']
            else:
                emp_name = 'N/A'

            if 'DebtorName' in results:
                debtor_name = results['DebtorName']
            else:
                debtor_name = 'N/A'

            if 'FileId' in results:
                file_id = results['FileId']
            else:
                file_id = 'N/A'

            if 'DiscssionType' in results:
                discussion_type = results['DiscssionType']
            else:
                discussion_type = 'N/A'

            if 'DebtorSentiment' in results:
                debtor_sentiment = results['DebtorSentiment']
            else:
                debtor_sentiment = 'N/A'


            data = {"summary_report": summary_report, "topics": topics, "foul_language": foul_language,
                    "action_items": action_items, "owners": owners, "sentiment_score": sentiment_score,
                    "average_sentiment": average_sentiment,"prompt": prompt,"reminder_message":reminder_message,"org_name":org_name,"debtor_name":debtor_name,"emp_name":emp_name,"file_id":file_id,"discussion_type":discussion_type,"debtor_sentiment":debtor_sentiment}
            return status, data
        except Exception as e:
            status = 'failure'
            self.logger.error(f" Sentiment Error in method get_sentiment",str(e))
            return status, set_json_format([str(e)], e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))

    def dump_data_into_sentiment_database(self, server_name, database_name, client_id,transcribe_data):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None:
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            try:
                prohibited_prompt_inject= self.get_prohibited_data_from_table(server_name, database_name, client_id)
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
                    status, sentiment_call_data = self.get_sentiment(transcribe_merged_string, prohibited_prompt_inject[0])
                    if status == 'success':
                        update_audio_transcribe_column_first_dump = {
                            AudioTranscribe.CaseID: str(sentiment_call_data["file_id"]),
                            AudioTranscribe.DebtorName: str(sentiment_call_data["debtor_name"]),
                            AudioTranscribe.AgentID: str(sentiment_call_data["emp_name"]),
                            AudioTranscribe.DiscussionType: str(sentiment_call_data["discussion_type"]),
                        }
                        session.query(AudioTranscribe).filter_by(AudioFileName=current_file).update(
                            update_audio_transcribe_column_first_dump)
                        session.commit()
                        dump_data_into_table = SentimentAnalysis(ClientId=clientid,
                                                                 AnalysisDateTime=analysis_sentiment_date, SentimentStatus=21,
                                                                 AudioFileName=current_file,Created=created_sentiment_date,
                                                                 SentimentScore=str(sentiment_call_data["sentiment_score"]),
                                                                 Modified=modified_sentiment_date,
                                                                 Sentiment=str(sentiment_call_data["average_sentiment"]),Summary=str(sentiment_call_data["summary_report"]),
                                                                 Topics=str(sentiment_call_data["topics"]),FoulLanguage=str(sentiment_call_data["foul_language"]),
                                                                 ActionItems=str(sentiment_call_data["action_items"]),Owners=str(sentiment_call_data["owners"]),
                                                                 prompt=str(sentiment_call_data["prompt"]),Reminder=str(sentiment_call_data["reminder_message"]),
                                                                 OrgName=str(sentiment_call_data["org_name"]),DebtorName=str(sentiment_call_data["debtor_name"]),
                                                                 EmployeeName=str(sentiment_call_data["emp_name"]),
                                                                 DebtorSentiment=str(sentiment_call_data["debtor_sentiment"]),

                                                                 )
                        session.add(dump_data_into_table)
                        session.commit()
                        result=set_json_format([], SUCCESS, True, f"Sentiment Record successfully recorded for the file {current_file}")
                        return result,SUCCESS
                    else:
                        return sentiment_call_data,RESOURCE_NOT_FOUND
                else:
                    #Update Logic
                    status, sentiment_call_data = self.get_sentiment(transcribe_merged_string, prohibited_prompt_inject[0])

                    if status == "success":
                        update_audio_transcribe_column_dic = {
                            AudioTranscribe.CaseID: str(sentiment_call_data["file_id"]),
                            AudioTranscribe.DebtorName: str(sentiment_call_data["debtor_name"]),
                            AudioTranscribe.AgentID: str(sentiment_call_data["emp_name"]),
                            AudioTranscribe.DiscussionType: str(sentiment_call_data["discussion_type"]),
                            }
                        session.query(AudioTranscribe).filter_by(AudioFileName=current_file).update(
                            update_audio_transcribe_column_dic)
                        session.commit()
                        update_column_dic = {SentimentAnalysis.Sentiment:str(sentiment_call_data["average_sentiment"]),
                                             SentimentAnalysis.Modified:modified_sentiment_date,
                                             SentimentAnalysis.SentimentScore:str(sentiment_call_data["sentiment_score"]),
                                             SentimentAnalysis.ActionItems:str(sentiment_call_data["action_items"]),
                                             SentimentAnalysis.Topics:str(sentiment_call_data["topics"]),SentimentAnalysis.Owners:str(sentiment_call_data["owners"]),
                                             SentimentAnalysis.FoulLanguage:str(sentiment_call_data["foul_language"]),
                                             SentimentAnalysis.prompt:str(sentiment_call_data["prompt"]),
                                             SentimentAnalysis.Reminder:str(sentiment_call_data["reminder_message"]),
                                             SentimentAnalysis.Summary:str(sentiment_call_data["summary_report"]),
                                             SentimentAnalysis.OrgName:str(sentiment_call_data["org_name"]),
                                             SentimentAnalysis.DebtorName:str(sentiment_call_data["debtor_name"]),
                                             SentimentAnalysis.EmployeeName:str(sentiment_call_data["emp_name"]),
                                             SentimentAnalysis.DebtorSentiment:str(sentiment_call_data["debtor_sentiment"]),
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
                return set_json_format(error_array, e.args[0].split(":")[1].split("-")[0].strip(), False, str(e)),RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in dump_data_into_sentiment_database or get_sentiment", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Sentiment Error in method get_sentiment", str(e))
                return set_json_format(error_array, e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))
            finally:
                session.close()

        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result, INTERNAL_SERVER_ERROR

    def get_data_from_transcribe_table(self, server_name, database_name, client_id,audio_file,transcribe_param):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            # if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            session_logger = self.global_utility.get_database_session(connection_string[0]['logger'])
            logger_handler = self.logger.log_entry_into_sql_table(session_logger, client_id, False)
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

                    if len(chunk_results_check) == 0:
                        data = {"status": RESOURCE_NOT_FOUND,"message": f":{audio_file} file not exist in AudioTranscribeTracker Table"}
                        return data, RESOURCE_NOT_FOUND

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
                if transcribe_param =="True":
                    return result,SUCCESS
                else:
                    transcribe_audio_data=''.join(transcribe_text)
                    # audion_transcribe_info = self.audio_client_info_through_prompt(transcribe_audio_data)
                    return self.audio_client_info_through_prompt(transcribe_audio_data)
            except Exception as e:
                self.logger.error(f": get_data_from_transcribe_table {e}",e)
                error_array = []
                error_array.append(str(e))
                self.logger.error('Error in Method get_data_from_transcribe_table ', str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
            finally:
                self.logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
                session.close()
                session_logger.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR



    def get_transcribe_data_for_sentiment(self, server_name, database_name, client_id,audio_file):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            # if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            session_logger = self.global_utility.get_database_session(connection_string[0]['logger'])
            logger_handler = self.logger.log_entry_into_sql_table(session_logger, client_id, False)
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
                    chunk_results_check = check_chunk_exist.all()

                    if len(chunk_results_check) == 0:
                        data = {"status": RESOURCE_NOT_FOUND,"message": f":{audio_file} file not exist in AudioTranscribeTracker Table"}
                        return data, RESOURCE_NOT_FOUND
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
                    data= {"status":RESOURCE_NOT_FOUND,"message":f":Record not found {audio_file} in AudioTranscribe Table"}
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
                self.logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
                session.close()
                session_logger.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def get_sentiment_data_from_table(self, server_name, database_name, client_id,audio_file):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            # if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            session_logger = self.global_utility.get_database_session(connection_string[0]['logger'])
            logger_handler = self.logger.log_entry_into_sql_table(session_logger, client_id, False)
            # session = self.global_utility.get_database_session(connection_string)
            check_audio_file_exits = session.query(SentimentAnalysis).filter(
                SentimentAnalysis.AudioFileName == audio_file).all()

            audio_file_size = session.query(AudioTranscribe.FileSize).filter(
                AudioTranscribe.AudioFileName == audio_file).first()[0]
            try:
                if len(check_audio_file_exits) > 0:
                    sentiment_dic={}
                    data = session.query(SentimentAnalysis).filter_by(AudioFileName=audio_file).all()
                    sentiment_dic.update({"ClientId":data[0].ClientId,
                                          "AnalysisDateTime":data[0].AnalysisDateTime,"AudioFileName":data[0].AudioFileName,
                                          "Created":data[0].Created,"SummaryReport":data[0].Summary,"Topics":data[0].Topics,
                                          "FoulLanguage":data[0].FoulLanguage,
                                          "ActionItemsOwners":data[0].Owners,
                                          "Modified":data[0].Modified,"Sentiment":data[0].Sentiment,"Reminder":data[0].Reminder,"FileDuration":audio_file_size})
                    # result = {"sentimentdata": sentiment_dic}
                    if bussiness_model == "cogent":
                        sentiment_dic = sentiment_dic
                    else:
                        del sentiment_dic["Reminder"]

                    result = sentiment_dic
                    self.logger.info(f":Get Data from SentimentAnalysis table successfully for AudioFile {audio_file}")
                    return result,SUCCESS
                else:
                    data = {"status":RESOURCE_NOT_FOUND,"message": f"Record not found {audio_file} in AudioTranscribe Table"}
                    self.logger.error(f"Record not found {audio_file} in AudioTranscribe Table", RESOURCE_NOT_FOUND)
                    return data,RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in get_sentiment_data_from_table", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Fetch record from Sentiment table Error in method get_sentiment_data_from_table", str(e))
                return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
                # self.logger.error(f": Error {e}",e)
            finally:
                self.logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
                session.close()
                session_logger.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def get_prohibited_data_from_table(self, server_name, database_name, client_id):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            # if len(connection_string) > 0:
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            session_logger = self.global_utility.get_database_session(connection_string[0]['logger'])
            logger_handler = self.logger.log_entry_into_sql_table(session_logger, client_id, False)
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
                    data = {"status":RESOURCE_NOT_FOUND,"message": f"Record not found {client_id} in ProhibitedKeyword Table"}
                    return data,RESOURCE_NOT_FOUND
            except Exception as e:
                self.logger.error(f"Found error in ProhibitedKeyword", str(e))
                error_array = []
                error_array.append(str(e))
                self.logger.error(f" Fetch record from Sentiment table Error in method get_sentiment_data_from_table", str(e))
                return set_json_format(error_array, RESOURCE_NOT_FOUND, False, str(e))
                # self.logger.error(f": Error {e}",e)
            finally:
                self.logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
                session.close()
                session_logger.close()
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR

    def calculate_max_tokens(self, text, token_size=1):

        words = text.split()
        tokens_count = len(words) * token_size
        return tokens_count

    def get_sentiment_data_from_table_by_column_name(self, server_name, database_name, client_id,column_name,column_value,report_type,page,per_page):
        connection_string, status = self.global_utility.get_connection_string(server_name, database_name, client_id)
        if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
            column = getattr(AudioTranscribe, column_name)
            session = self.global_utility.get_database_session(connection_string[0]['transaction'])
            session_logger = self.global_utility.get_database_session(connection_string[0]['logger'])
            logger_handler = self.logger.log_entry_into_sql_table(session_logger, client_id, False)
            audio_file = session.query(AudioTranscribe.AudioFileName).filter(column==column_value)
            offset = (page - 1) * per_page
            query = audio_file.order_by(AudioTranscribe.Id)
            offset_data = query.offset(offset).limit(per_page).all()
            sentiment_dic = {}
            merged_data = []
            for audio_file_val, in offset_data:
                check_audio_file_exits = session.query(SentimentAnalysis).filter(SentimentAnalysis.AudioFileName == audio_file_val).all()
                try:
                    if len(check_audio_file_exits) > 0:
                        data = session.query(SentimentAnalysis).filter_by(AudioFileName=audio_file_val).all()

                        if report_type=="call_summary":
                            sentiment_dic.update({"AudioFileName":data[0].AudioFileName,"SummaryReport":data[0].Summary})
                            merged_data.append(sentiment_dic)
                            sentiment_dic={}
                        elif report_type=="sentiment":
                            sentiment_dic.update({"AudioFileName":data[0].AudioFileName,"Summary Topics":data[0].Topics,"FoulLanguage":data[0].FoulLanguage,"Sentiment":data[0].Sentiment})
                            merged_data.append(sentiment_dic)
                            sentiment_dic = {}
                        elif report_type=="call_analysis":
                            sentiment_dic.update({"AudioFileName":data[0].AudioFileName,"Summary":data[0].Summary,"ActionItems":data[0].Owners,"Topics":data[0].Topics})
                            merged_data.append(sentiment_dic)
                            sentiment_dic = {}
                        else:
                            sentiment_dic.update({"ClientId":data[0].ClientId,
                                                  "AnalysisDateTime":data[0].AnalysisDateTime,"AudioFileName":data[0].AudioFileName,
                                                  "Created":data[0].Created,"SummaryReport":data[0].Summary,"Topics":data[0].Topics,
                                                  "FoulLanguage":data[0].FoulLanguage,
                                                  "ActionItemsOwners":data[0].Owners,
                                                  "Modified":data[0].Modified,"Sentiment":data[0].Sentiment,"Reminder":data[0].Reminder})
                            merged_data.append(sentiment_dic)
                            sentiment_dic={}
                        self.logger.info(f":Get Data from SentimentAnalysis table successfully for AudioFile {audio_file}")
                    else:
                        data = {"status":RESOURCE_NOT_FOUND,"message": f"Record not found {column_name} {column_value} in AudioTranscribe Table"}
                        self.logger.error(f"Record not found {column_name}{column_value} in AudioTranscribe Table", RESOURCE_NOT_FOUND)
                        return data,RESOURCE_NOT_FOUND
                except Exception as e:
                    self.logger.error(f"Found error in get_sentiment_data_from_table", str(e))
                    error_array = []
                    error_array.append(str(e))
                    self.logger.error(f" Fetch record from Sentiment table Error in method get_sentiment_data_from_table", str(e))
                    return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
                    # self.logger.error(f": Error {e}",e)
                finally:
                    self.logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
                    session.close()
                    session_logger.close()
            return merged_data
        else:
            result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
            return result,INTERNAL_SERVER_ERROR


    def audio_client_info_through_prompt(self,text):
        try:
            status = 'success'
            prompt = "{}.@@@. {}".format(prompt_data.audio_transcribe_prompt,text)
            response = client.chat.completions.create(
                model=open_ai_model,
                messages=[
                    # {"role": "system", "content": prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                n=1,
                presence_penalty=0.8,
                temperature=0.2,
                top_p=0.8,
                stop=None
                # stop=["\n"]
            )
            sentiment = response.choices[0].message.content
            json_string_cleaned = sentiment.replace('```', '').replace('\n', '').replace('json', '')
            results = json.loads(json_string_cleaned)

            if 'OrganisationName' in results:
                org_name = results['OrganisationName']
            else:
                org_name = 'N/A'

            if 'EmployeeName' in results:
                emp_name = results['EmployeeName']
            else:
                emp_name = 'N/A'

            if 'DebtorName' in results:
                debtor_name = results['DebtorName']
            else:
                debtor_name = 'N/A'

            if 'FileId' in results:
                file_id = results['FileId']
            else:
                file_id = 'N/A'

            if 'DiscssionType' in results:
                discussion_type = results['DiscssionType']
            else:
                discussion_type = 'N/A'

            if 'DebtorSentiment' in results:
                debtor_sentiment = results['DebtorSentiment']
            else:
                debtor_sentiment = 'N/A'

            data = {"org_name":org_name,"debtor_name":debtor_name,"emp_name":emp_name,"file_id":file_id,"discussion_type":discussion_type,"debtor_sentiment":debtor_sentiment}
            return {"data":data,"status":SUCCESS},SUCCESS
        except Exception as e:
            status = 'failure'
            self.logger.error(f" Error in method audio_client_info_through_prompt",str(e))
            return status, set_json_format([str(e)], e.args[0].split(":")[1].split("-")[0].strip(), False, str(e))