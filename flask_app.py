import os
from flask import Flask, request,render_template,send_file, abort, make_response,url_for,redirect,jsonify
from app.configs.error_code_enum import *
from flask_cors import CORS
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
CORS(app)
from database_query_utils import DBRecord
from flask_end_points_service import (get_json_format, set_json_format, get_token_based_authentication, get_app_configurations,update_authentication_token,generate_authentication_token,
                                      update_audio_transcribe_table, copy_audio_files_process, update_audio_transcribe_tracker_table,
                                      get_client_master_table_configurations, get_audio_transcribe_tracker_table_data, get_file_name_pattern,open_ai_transcribe_audio,
                                      get_ldap_authentication, get_audio_transcribe_table_data, update_transcribe_audio_text, get_all_configurations_table,open_source_transcribe_audio)


from common_utils import get_data_multi_transcribe,get_job_staus_from_audiotranscribe_table,get_audio_file_name_from_table


from authenticaion_process import register_user,login_method,unlock_account

from flask_bcrypt import Bcrypt
import secrets
from datetime import timedelta, datetime
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity,get_jwt,verify_jwt_in_request
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secret key of your choice
# app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # Change this to a secret key of your choice
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db_instance = DBRecord()
server_name = os.environ.get("SERVER_NAME")
# Below configuration dev environment while running application in Dev Environment
database_name = os.environ.get("DATABASE_NAME_DEV")
# Below configuration QA environment while running application in QA Environment
#database_name = os.environ.get("DATABASE_NAME_QA")

from app.model.sentiment_analysis import SentimentAnalysisCreation
sentiment_instance = SentimentAnalysisCreation()
from app.model.compliance_analysis import ComplianceAnalysisCreation
compliance_instance = ComplianceAnalysisCreation()

from app import prompt_check_list

from functools import wraps

from db_layer.models import LoginDetails
def check_authorization(func):
    access_token = os.environ.get("access_token")
    if access_token == "Yes":
        @wraps(func)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            get_jwt_identity()
            from flask import request
            token = request.headers.get('Authorization')
            client_id = request.headers.get('clientid')
            remove_bearer = token.split()[1]
            connection_string, status = compliance_instance.global_utility.get_connection_string(server_name, database_name, client_id)
            if status == SUCCESS and connection_string[0]['transaction'] != None and connection_string[0]['logger'] != None:
                session = compliance_instance.global_utility.get_database_session(connection_string[0]['transaction'])
                get_refresh_token = session.query(LoginDetails.refresh_token).filter_by(token=remove_bearer).first()[0]
                get_client_identifier_from_db = session.query(LoginDetails.clientIdentifier).filter_by(token=remove_bearer).first()[0]
                from authenticaion_process import get_exp_token_from_database
                import hashlib
                from flask import request
                check_refresh_token_status = get_exp_token_from_database(get_refresh_token)
                client_identifier = hashlib.sha256(request.remote_addr.encode()).hexdigest()
                if check_refresh_token_status["status"] == 'expire' and client_identifier == get_client_identifier_from_db:
                    return jsonify({'status': "Token has been expired.Please re-login Again"})
            else:
                return jsonify({'status': INTERNAL_SERVER_ERROR, "message": "Unable to connect to the database"})
            return func(*args, **kwargs)
    else:
        @wraps(func)
        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)

    return decorated_function


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
@check_authorization
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
@check_authorization
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
@check_authorization
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
@check_authorization
def get_transcribe_sentiment():
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
@check_authorization
def get_sentiment_data():
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
@check_authorization
def dump_data_sentiment_table():
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
    if len(prompt_check_list.open_ai_key) > 0:
        data = sentiment_instance.get_transcribe_data_for_sentiment(server_name, database_name, client_id,audio_file_name)
        return data
    else:
        data={"message":"Open AI key can't be blank","status":RESOURCE_NOT_FOUND}
        return data,RESOURCE_NOT_FOUND


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
@check_authorization
def dump_data_compliance_table():
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
    if len(prompt_check_list.open_ai_key) > 0:
        data = compliance_instance.get_transcribe_data_for_compliance(server_name, database_name, client_id,audio_file_name)
        return data
    else:
        data={"message":"Open AI key can't be blank","status":RESOURCE_NOT_FOUND}
        return data,RESOURCE_NOT_FOUND


@app.route('/get_data_from_compliance_score', methods=['GET'])
@check_authorization
def get_compliance_score_data():
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
@check_authorization
def get_compliance_data():
    client_id_val = request.args.get('clientid')
    try:
        client_id = int(client_id_val)
        audio_file_name = request.args.get('audio_file')
        data = compliance_instance.get_compliance_data_from_table(server_name, database_name, client_id,audio_file_name)
    except Exception as e:
        response_message = 'You were given the wrong parameter by them. Please try again with a valid parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    return data


@app.route('/compliance',methods=['GET'])
def compliance_data():
    return render_template('compliance.html')

@app.route('/sentiment_data_by_report_type', methods=['GET','POST'])
@check_authorization
def get_sentiment_data_by_report_type():
    client_id_val = request.args.get('clientid')
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')
    report_type = request.args.get('report_type')
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
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
    try:
        data = sentiment_instance.get_sentiment_data_from_table_by_column_name(server_name, database_name, client_id,column_name,column_value,report_type,page,per_page)
    except Exception as e:
        response_message = 'Invalid column name parameter.Please try again with a valid parameter.'
        return {
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    return data

@app.route('/multi_compliance_reports', methods=['GET','POST'])
@check_authorization
def get_compliance_data_by_column_name():
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
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    try:
        data = compliance_instance.get_compliance_data_by_report_type(server_name, database_name, client_id,column_name,column_value,page,per_page)
    except Exception as e:
        response_message = 'Invalid column name parameter.Please try again with a valid parameter.'
        return {
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND
    return data


@app.route('/multi_transcribe_text', methods=['GET','POST'])
@check_authorization
def get_transcribe_multi_data():
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
    # audio_file_name = request.args.get('audio_file')
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    data = get_data_multi_transcribe(server_name, database_name, client_id,column_name,column_value,page,per_page)
    return data


BASE_DIRECTORY = "C:/AICogent/ICFiles/Done/"

@app.route('/download/<path:filename>', methods=['GET'])
@check_authorization
def download_files(filename):

    safe_path = os.path.abspath(os.path.join(BASE_DIRECTORY, filename))
    if os.path.commonprefix([safe_path, os.path.abspath(BASE_DIRECTORY)]) == os.path.abspath(BASE_DIRECTORY):
        if os.path.exists(safe_path):
            print("File successfully downloaded")
            send_file(safe_path, as_attachment=True)
            response = make_response(send_file(safe_path, as_attachment=True))
            response.headers['X-Success-Message'] = 'File successfully downloaded'
            # data = {'response':response,'message':'File successfully  downloaded'}
            return response
        else:
            abort(404, description="File not found")
    else:
        abort(403, description="Access denied")

@app.route('/get_audio_filename', methods=['GET'])
@check_authorization
def get_all_audio_file():
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
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    data = get_audio_file_name_from_table(server_name, database_name, client_id, column_name,column_value, page, per_page)
    return data

@app.route('/get_job_status', methods=['GET'])
@check_authorization
def get_call_status():
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
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    to_date = request.args.get('to_date')
    from_date = request.args.get('from_date')
    data = get_job_staus_from_audiotranscribe_table(server_name, database_name, client_id, column_name,column_value, page, per_page,from_date,to_date)
    return data

UPLOAD_FOLDER = 'C:/AICogent/ICFiles/'
ALLOWED_EXTENSIONS = {'wav','mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    files = request.files.getlist('file')
    if not files:
        return jsonify({'error': 'No selected files'}), 400

    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_files.append(filename)
        else:
            return jsonify({'error': f'File type not allowed: {file.filename}'}), 400
    return jsonify({'message': f'Files uploaded successfully!', 'files': uploaded_files}), 200


@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f'File {filename} uploaded successfully!'

@app.route('/register', methods=['GET','POST'])
def register():
    username=request.headers.get('username')
    password=request.headers.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    client_id_val=request.headers.get('clientid')
    if client_id_val and username:
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
        result = register_user(server_name, database_name, client_id,username,hashed_password)
        return result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/login', methods=['GET','POST'])
def login():
    username = request.headers.get('username')
    password = request.headers.get('password')
    client_id_val = request.headers.get('clientid')
    if client_id_val and username:
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
        data = login_method(server_name, database_name, client_id,username,password)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
                   "result": [response_message],
                   "message": response_message,
                   "status": 'failed',
                   'status_code': RESOURCE_NOT_FOUND
               }, RESOURCE_NOT_FOUND

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.headers.get('username')
    password = request.headers.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    client_id_val = request.headers.get('clientid')
    data = unlock_account(server_name, database_name, client_id_val, username, hashed_password)
    return data

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(threaded=True)
