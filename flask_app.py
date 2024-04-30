import os
from flask import Flask, request,render_template
from app.configs.error_code_enum import *
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from database_query_utils import DBRecord
from flask_end_points_service import (get_json_format, set_json_format, get_token_based_authentication, get_app_configurations,update_authentication_token,generate_authentication_token,
                                      update_audio_transcribe_table, copy_audio_files_process, update_audio_transcribe_tracker_table,
                                      get_client_master_table_configurations, get_audio_transcribe_tracker_table_data, get_file_name_pattern,open_ai_transcribe_audio,
                                      get_ldap_authentication, get_audio_transcribe_table_data, update_transcribe_audio_text, get_all_configurations_table,open_source_transcribe_audio)


db_instance = DBRecord()
server_name = 'FLM-VM-COGAIDEV'
#database_name = 'AudioTrans'
database_name = 'AudioMaster'



@app.route('/get_all_data', methods=['GET','POST'])
def get_record():
    table_name = request.args.get('table_name')
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    # data = db_instance.get_all_record_by_proc(server_name, database_name, client_id, table_name.capitalize())
    data = db_instance.get_all_record(server_name, database_name, client_id,table_name.capitalize())
    return data


@app.route('/get_record_by_id', methods=['GET','POST'])
def get_recordby_id():
    table_name = request.args.get('table_name')
    # client_id = int(request.args.get('clientid'))
    id = request.args.get('id')
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    data = db_instance.get_record_by_id(server_name, database_name, client_id,table_name, id)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/get_record_by_column_name', methods=['GET','POST'])
def get_recordby_column_name():
    table_name = request.args.get('table_name')
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')
    data = db_instance.get_data_by_column_name(server_name, database_name, client_id,table_name, column_name, column_value)
    return data


@app.route('/update_record_by_column', methods=['GET','POST'])
def get_update_by_column_name():
    table_name = request.args.get('table_name')
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    column_to_update = request.args.get('column_to_update')
    new_value = request.args.get('new_value')
    condition_column = request.args.get('condition_column')
    condition_value = request.args.get('condition_value')

    data = db_instance.update_record_by_column(server_name, database_name, client_id,table_name, column_to_update, new_value, condition_column,
                                               condition_value)

    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/delete_record_by_id', methods=['DELETE'])
def delete_recordby_id():
    table_name = request.args.get('table_name')
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    itm_id = request.args.get('id')
    data = db_instance.delete_record_by_id(server_name, database_name, client_id,table_name, itm_id)

    # data = db_instance.delete_record_by_id(table_name, itm_id)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return {'data': data}


@app.route('/merge_chunk_transcribe_text', methods=['GET','POST'])
def get_transcribe_sentiment():
    from app.model.sentiment_analysis import SentimentAnalysisCreation
    sentiment_instance = SentimentAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    data = sentiment_instance.get_data_from_transcribe_table(server_name, database_name, client_id,audio_file_name)
    return data


@app.route('/get_client_master_configurations', methods=['GET','POST'])
def get_client_master_configurations():
    # Done
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    json_result = get_client_master_table_configurations(server_name, database_name, client_id)
    return json_result


@app.route('/get_client_configurations', methods=['GET','POST'])
def get_client_configurations():
    # Done
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    json_result = get_app_configurations(server_name, database_name, client_id)
    return json_result


@app.route('/get_audio_transcribe_data', methods=['GET','POST'])
def get_audio_transcribe_data():
    try:
        # Done
        client_id_val = request.args.get('clientid')
        try:
            client_id = int(client_id_val)
        except Exception as e:
            response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
            return {
                "result": [response_message],
                "message": response_message,
                "status": 'failed',
                'status_code': RESOURCE_NOT_FOUND
            }, RESOURCE_NOT_FOUND
        json_result = get_audio_transcribe_table_data(server_name, database_name, client_id)
        return json_result
    except Exception as e:
        return get_json_format([], False, e)


@app.route('/get_audio_transcribe_tracker_data', methods=['GET','POST'])
def get_audio_transcribe_tracker_data():
    try:
        # Done
        client_id_val = request.args.get('clientid')
        try:
            client_id = int(client_id_val)
        except Exception as e:
            response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
            return {
                "result": [response_message],
                "message": response_message,
                "status": 'failed',
                'status_code': RESOURCE_NOT_FOUND
            }, RESOURCE_NOT_FOUND
        audio_id = int(request.args.get('audioid'))
        current_user = os.getlogin()
        json_result = get_audio_transcribe_tracker_table_data(server_name, database_name, client_id, audio_id)
        return json_result
    except Exception as e:
        return get_json_format([],INTERNAL_SERVER_ERROR, False, str(e)),INTERNAL_SERVER_ERROR


@app.route('/add_update_transcribe', methods=['GET','POST'])
def add_update_transcribe():
    #  Dev Done, testing pending
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    recored_id = int(request.args.get('id'))
    updatevalues = request.args.get('updatevalues')
    update_status = update_audio_transcribe_table(server_name, database_name, client_id, recored_id, updatevalues)
    return update_status


@app.route('/add_update_transcribe_tracker', methods=['GET','POST'])
def add_update_transcribe_tracker():
    #  Dev Done, testing pending
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    recored_id = int(request.args.get('id'))
    updatevalues = request.args.get('updatevalues')
    update_status = update_audio_transcribe_tracker_table(server_name, database_name, client_id, recored_id,
                                                          updatevalues)
    return update_status

@app.route('/get_data_from_sentiment_table', methods=['GET','POST'])
def get_sentiment_data():
    from datetime import datetime
    print("Start get_sentiment_data End Point time:-", datetime.now())
    from app.model.sentiment_analysis import SentimentAnalysisCreation
    sentiment_instance = SentimentAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    data = sentiment_instance.get_sentiment_data_from_table(server_name, database_name, client_id,audio_file_name)
    return data


@app.route('/get_all_configurations', methods=['GET','POST'])
def get_all_configurations():
    #  Dev Done
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    current_user = os.getlogin()
    print('Current login user:', current_user)
    json_result = get_all_configurations_table(server_name, database_name, client_id)
    return json_result

@app.route('/copy_audio_files', methods=['GET','POST'])
def copy_audio_files():
    #  Dev Done
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    current_user = os.getlogin()
    print('Current login user:', current_user)
    json_result = copy_audio_files_process(server_name, database_name, client_id)
    return json_result

@app.route('/transcribe_audio_text', methods=['GET','POST'])
def transcribe_audio_text():
    client_id_val = request.args.get('clientid')
    record_id_val = request.args.get('id')
    try:
        client_id = int(client_id_val)
        record_id = int(record_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

    json_result = update_transcribe_audio_text(server_name, database_name, client_id, record_id)
    return json_result



@app.route('/match_file_name_pettern', methods=['GET','POST'])
def match_file_name_pettern():
    #  Dev Done
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    file_name = request.args.get('filename')
    current_user = os.getlogin()
    file_name = '24-10003-douglas-21March-AY-Noida-Call-Approva-Ashutosh'
    file_name = '24-10003_tomous_25April_CTS_Mumbai_Outbound_Ritesh_Manish'
    # file_name = 'ABC-21March-AY-Noida-Call-Approva'
    print('Current login user:', current_user)
    json_result = get_file_name_pattern(server_name, database_name, client_id,file_name)
    return json_result

@app.route('/dump_data_into_sentiment', methods=['GET','POST'])
def dump_data_sentiment_table():
    from app.model.sentiment_analysis import SentimentAnalysisCreation
    sentiment_instance = SentimentAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    data = sentiment_instance.get_transcribe_data_for_sentiment(server_name, database_name, client_id,audio_file_name)
    return data

@app.route('/open_ai_transcribe_audio_text', methods=['GET','POST'])
def open_ai_transcribe_audio_text():
    client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    # file = 'D:/Cogent_AI_Audio_Repo/DMV-85311-MU1/DMV-85311-MU11_Chunk_6.wav'
    file = 'D:/Cogent_AI_Audio_Repo/DMV-85311-MU1/Outbound_FollowUpCall-Z1.wav'
    transcript, status  = open_ai_transcribe_audio(file)
    if status == SUCCESS:
        data = {"text": transcript,'status': SUCCESS}
        return transcript,status
    return_data = {"text": 'no transcript', 'status': "500"}
    return transcript,status
@app.route('/open_source_transcribe', methods=['GET','POST'])
def open_source_transcribe():
    client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    file = 'D:/Cogent_AI_Audio_Repo/Outbound_DebtDispute/Outbound_DebtDispute.mp3'
    transcript, status  = open_source_transcribe_audio(file)
    if status == SUCCESS:
        data = {"text": transcript,'status': SUCCESS}
        return transcript,status
    return_data = {"text": 'no transcript', 'status': "500"}
    return transcript,status


@app.route('/token_authenticate', methods=['GET','POST'])
def token_authenticate():
    #  Dev Done, testing pending
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    user_name = request.args.get('username')
    current_user = os.getlogin()
    print('Current login user:', current_user)
    result = get_token_based_authentication(server_name, database_name, client_id, user_name)
    return result

@app.route('/ldap_authenticate', methods=['GET','POST'])
def ldap_authenticate():
    #  Dev Done, testing pending
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    current_user = os.getlogin()
    print('Current login user:', current_user)
    result = get_ldap_authentication(server_name, database_name, client_id)
    return result

@app.route('/update_token', methods=['GET','POST'])
def update_token():
    #  Dev Done, testing pending
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    user_name = request.args.get('username')
    current_user = os.getlogin()
    print('Current login user:', current_user)
    result = update_authentication_token(server_name, database_name, client_id,user_name)
    return result

@app.route('/new_token', methods=['GET','POST'])
def new_token():
    #  Dev Done, testing pending
    # client_id = int(request.args.get('clientid'))
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    user_name = request.args.get('username')
    current_user = os.getlogin()
    print('Current login user:', current_user)
    result = generate_authentication_token(server_name, database_name, client_id,user_name)
    return result

@app.route('/sentiment',methods=['GET'])
def sentiment_data():
    return render_template('sentiment_data.html')

@app.route('/transcribe',methods=['GET'])
def merge_transcribe():
    return render_template('merged_chunk_data.html')


@app.route('/get_prohibited_data_from_table', methods=['GET'])
def get_prohibited_data():
    from app.model.sentiment_analysis import SentimentAnalysisCreation
    sentiment_instance = SentimentAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    data = sentiment_instance.get_prohibited_data_from_table(server_name, database_name, client_id)
    return data

@app.route('/dump_data_into_compliance', methods=['GET','POST'])
def dump_data_compliance_table():
    from app.model.compliance_analysis import ComplianceAnalysisCreation
    compliance_instance = ComplianceAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    data = compliance_instance.get_transcribe_data_for_compliance(server_name, database_name, client_id,audio_file_name)
    return data


@app.route('/get_data_from_compliance_score', methods=['GET'])
def get_compliance_score_data():
    from app.model.compliance_analysis import ComplianceAnalysisCreation
    compliance_instance = ComplianceAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    data = compliance_instance.get_data_from_compliance_score(server_name, database_name, client_id)
    return data


@app.route('/get_data_from_compliance_table', methods=['GET'])
def get_compliance_data():
    from app.model.compliance_analysis import ComplianceAnalysisCreation
    compliance_instance = ComplianceAnalysisCreation()
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    # client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    data = compliance_instance.get_compliance_data_from_table(server_name, database_name, client_id,audio_file_name)
    return data


@app.route('/compliance',methods=['GET'])
def compliance_data():
    return render_template('compliance.html')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(threaded=True)
