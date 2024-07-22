from app.services.logger import Logger
from sqlalchemy import create_engine,desc,and_
from app.db_connection import DbConnection
from app.utilities.utility import GlobalUtility
from app.configs.error_code_enum import *
from sqlalchemy.orm import sessionmaker

from flask_end_points_service import get_connection_string
from flask_end_points_service import get_json_format,set_json_format

from db_layer.models import AudioTranscribe, AudioTranscribeTracker

global_utility = GlobalUtility()
logger = Logger()
db_connection = DbConnection()


def get_database_session(connection_string):
    try:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except Exception as e:
        return get_json_format([], False, e)

def get_job_staus_from_audiotranscribe_table(server_name, database_name, client_id, column_name, column_value, page,
                                   per_page,from_date,to_date):
    connection_string, status = global_utility.get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        session = get_database_session(connection_string[0]['transaction'])
        session_logger = get_database_session(connection_string[0]['logger'])
        logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
        try:
            column = getattr(AudioTranscribe, column_name)
            audio_file = session.query(
                        AudioTranscribe.AudioFileName,
                        AudioTranscribe.JobStatus,
                        AudioTranscribe.SADone,
                        AudioTranscribe.SCDone
                    ).filter(
                        and_(
                            column== column_value,
                            AudioTranscribe.Created >= from_date,
                            AudioTranscribe.Created <= to_date)
                        ).order_by(desc(AudioTranscribe.Created))
            offset = (page - 1) * per_page
            query = audio_file.order_by(AudioTranscribe.Id)
            offset_data = query.offset(offset).limit(per_page).all()
            data_update ={}
            merged_data=[]
            for record in offset_data:
                if record[1]==3:
                    trans_status='Done'
                else:
                    trans_status ='Inprogress'

                if record[2]==True:
                    sc_status="Done"
                else:
                    sc_status ="Inprogress"

                if record[3]==True:
                    compliance_status="Done"
                else:
                    compliance_status="False"
                data_update.update({"AudioFIleName":record[0],"TranscribeStatus":trans_status,"CallAnanlysis":sc_status,"ComplianceStatus":compliance_status})
                merged_data.append(data_update)
                data_update={}
            return merged_data
        except Exception as e:
            logger.error(f": get_call_staus_from_audiotranscribe_table {e}", e)
            error_array = []
            error_array.append(str(e))
            logger.error('Error in Method get_call_staus_from_audiotranscribe_table ', str(e))
            return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR

def get_audio_file_name_from_table(server_name, database_name, client_id, column_name, column_value, page,
                                   per_page):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        session = get_database_session(connection_string[0]['transaction'])
        session_logger = get_database_session(connection_string[0]['logger'])
        logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
        column = getattr(AudioTranscribe, column_name)
        audio_file = session.query(AudioTranscribe.TranscribeFilePath).filter(column == column_value)
        # query_res = audio_file.all() # For all record
        offset = (page - 1) * per_page
        query = audio_file.order_by(AudioTranscribe.Id)
        offset_data = query.offset(offset).limit(per_page).all()
        data = [x.split("\\")[3] for x, in offset_data]
        return data
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result, INTERNAL_SERVER_ERROR

def get_data_multi_transcribe(server_name, database_name, client_id,column_name,column_value,page,per_page):
    connection_string, status = get_connection_string(server_name, database_name, client_id)
    if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
        session = get_database_session(connection_string[0]['transaction'])
        session_logger = get_database_session(connection_string[0]['logger'])
        logger_handler = logger.log_entry_into_sql_table(session_logger, client_id, False)
        column = getattr(AudioTranscribe, column_name)
        audio_file = session.query(AudioTranscribe.AudioFileName).filter(column == column_value)
        offset = (page - 1) * per_page
        query = audio_file.order_by(AudioTranscribe.Id)
        offset_data = query.offset(offset).limit(per_page).all()
        merged_data = []
        multi_trans_dic = {}

        try:
            audio_dictionary = {}
            transcribe_text = []
            trans_dic={}
            for audio_file_val, in offset_data:
                check_audio_id_exits = session.query(AudioTranscribe).filter_by(
                   AudioFileName = audio_file_val).all()
                if len(check_audio_id_exits) > 0:
                    audio_id_query = session.query(AudioTranscribe.Id).filter_by(
                        AudioFileName = audio_file_val)
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
                            # print("row outpupt", row.ClientId)
                            transcribe_text.append(row.ChunkText)
                            audio_dictionary.update({"ClientId": row.ClientId, "TranscribeId": row.AudioId,
                                                     "ChunkSequence": row.ChunkSequence,
                                                     "TranscribeMergeText": transcribe_text})
                        multi_trans_dic.update({"AudioFilename": audio_file_val, "TranscribeMergeText": transcribe_text[0]})
                        merged_data.append(multi_trans_dic)
                        multi_trans_dic={}
                    else:
                        logger.info(f":ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table")
                        data = {"status":RESOURCE_NOT_FOUND,"message": f"ChunkText is not exist for {audio_file} in AudioTranscribeTracker Table"}
                        return data,RESOURCE_NOT_FOUND
                else:
                    logger.info(f":Record not found {audio_file} in AudioTranscribe Table")
                    data = {"message": f"Record not found {audio_file} in AudioTranscribe Table","status":RESOURCE_NOT_FOUND}
                    return data,RESOURCE_NOT_FOUND
        except Exception as e:
            logger.error(f": get_data_from_transcribe_table {e}",e)
            error_array = []
            error_array.append(str(e))
            logger.error('Error in Method get_data_from_transcribe_table ', str(e))
            return set_json_format(error_array, INTERNAL_SERVER_ERROR, False, str(e))
        finally:
            logger.log_entry_into_sql_table(session_logger, client_id, True,logger_handler)
            session.close()
            session_logger.close()
        return merged_data, SUCCESS
    else:
        result = {'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"}
        return result,INTERNAL_SERVER_ERROR
