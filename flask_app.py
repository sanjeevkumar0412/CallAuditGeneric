import os
from flask import Flask, request,render_template,jsonify
from app.configs.error_code_enum import *
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from app.database_query_utils import DBRecord
from flask_end_points_service import (get_json_format, set_json_format, get_token_based_authentication, get_app_configurations,update_authentication_token,generate_authentication_token,
                                      update_audio_transcribe_table, copy_audio_files_process, update_audio_transcribe_tracker_table,
                                      get_client_master_table_configurations, get_audio_transcribe_tracker_table_data, get_file_name_pattern,open_ai_transcribe_audio,
                                      get_ldap_authentication, get_audio_transcribe_table_data, update_transcribe_audio_text, get_all_configurations_table,open_source_transcribe_audio)

from authenticaion_process import register_user,login_method,unlock_account
from flask_bcrypt import Bcrypt
import secrets
from datetime import timedelta, datetime
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity,get_jwt,verify_jwt_in_request
# app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to a secret key of your choice
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # Change this to a secret key of your choice
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
db_instance = DBRecord()
server_name = os.environ.get("SERVER_NAME")
# Below configuration dev environment while running application in Dev Environment
# database_name = os.environ.get("DATABASE_NAME_DEV")
database_name = os.environ.get("DATABASE_NAME_DEV")
# Below configuration QA environment while running application in QA Environment
#database_name = os.environ.get("DATABASE_NAME_QA")
from app.db_layer.models import RegisterUser

from app.model.sentiment_analysis import SentimentAnalysisCreation
sentiment_instance = SentimentAnalysisCreation()
from app.model.compliance_analysis import ComplianceAnalysisCreation
compliance_instance = ComplianceAnalysisCreation()

from app import prompt_check_list



@app.route('/get_all_data', methods=['GET','POST'])
def get_record():
    table_name = request.args.get('table_name')
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and table_name and user_name:
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
        data = db_instance.get_all_record(server_name, database_name, client_id,user_name,table_name.capitalize())
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_record_by_id', methods=['GET','POST'])
def get_recordby_id():
    table_name = request.args.get('table_name')
    id = request.args.get('id')
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and id and table_name and user_name:
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
        data = db_instance.get_record_by_id(server_name, database_name, client_id,user_name,table_name, id)
        if data == None:
            data = {"Error": "Invalid table/Data not available for this " + table_name}
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_record_by_column_name', methods=['GET','POST'])
def get_recordby_column_name():
    table_name = request.args.get('table_name')
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and id and table_name and user_name:
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
        data = db_instance.get_data_by_column_name(server_name, database_name, client_id,user_name,table_name, column_name, column_value)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/update_record_by_column', methods=['GET','POST'])
def get_update_by_column_name():
    table_name = request.args.get('table_name')
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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

        data = db_instance.update_record_by_column(server_name, database_name, client_id,user_name,table_name, column_to_update, new_value, condition_column,
                                                   condition_value)

        if data == None:
            data = {"Error": "Invalid table/Data not available for this " + table_name}
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
                }, RESOURCE_NOT_FOUND


@app.route('/delete_record_by_id', methods=['DELETE'])
def delete_recordby_id():
    table_name = request.args.get('table_name')
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        data = db_instance.delete_record_by_id(server_name, database_name, client_id,user_name,table_name, itm_id)
        if data == None:
            data = {"Error": "Invalid table/Data not available for this " + table_name}
        return {'data': data}
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/merge_chunk_transcribe_text', methods=['GET','POST'])
def get_transcribe_sentiment():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        audio_file_name = request.args.get('audio_file')
        data = sentiment_instance.get_data_from_transcribe_table(server_name, database_name, client_id,user_name,audio_file_name)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_client_master_configurations', methods=['GET','POST'])
def get_client_master_configurations():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        json_result = get_client_master_table_configurations(server_name, database_name, client_id,user_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/get_client_configurations', methods=['GET','POST'])
def get_client_configurations():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        json_result = get_app_configurations(server_name, database_name, client_id,user_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_audio_transcribe_data', methods=['GET','POST'])
def get_audio_transcribe_data():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        json_result = get_audio_transcribe_table_data(server_name, database_name, client_id,user_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND



@app.route('/get_audio_transcribe_tracker_data', methods=['GET','POST'])
def get_audio_transcribe_tracker_data():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        json_result = get_audio_transcribe_tracker_table_data(server_name, database_name, client_id,user_name, audio_id)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND



@app.route('/add_update_transcribe', methods=['GET','POST'])
def add_update_transcribe():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        update_status = update_audio_transcribe_table(server_name, database_name, client_id,user_name, recored_id, updatevalues)
        return update_status
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/add_update_transcribe_tracker', methods=['GET','POST'])
def add_update_transcribe_tracker():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        update_status = update_audio_transcribe_tracker_table(server_name, database_name, client_id,user_name, recored_id,
                                                              updatevalues)
        return update_status
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_data_from_sentiment_table', methods=['GET','POST'])
@jwt_required()
def get_sentiment_data():
    current_user = get_jwt_identity()
    print("current_user>>>>>>>>>>>", current_user)
    client_id_val = request.args.get('clientid')
    # user_name = request.args.get('username')
    audio_file_name = request.args.get('audio_file')
    access_token = request.headers.get('Authorization')
    remove_bearer = access_token.split()[1]

    if client_id_val and audio_file_name:
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
        data = sentiment_instance.get_sentiment_data_from_table(server_name, database_name, client_id,audio_file_name,remove_bearer)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND



@app.route('/get_all_configurations', methods=['GET','POST'])
def get_all_configurations():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        # print('Current login user:', current_user)
        json_result = get_all_configurations_table(server_name, database_name, client_id,user_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/copy_audio_files', methods=['GET','POST'])
def copy_audio_files():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        # print('Current login user:', current_user)
        json_result = copy_audio_files_process(server_name, database_name, client_id,user_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/match_file_name_pettern', methods=['GET','POST'])
def match_file_name_pettern():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    file_name = request.args.get('filename')
    if client_id_val and user_name and file_name:
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
        # current_user = os.getlogin()
        file_name = '24-10003-douglas-21March-AY-Noida-Call-Approva-Ashutosh'
        file_name = '24-10003_tomous_25April_CTS_Mumbai_Outbound_Ritesh_Manish'
        # file_name = 'ABC-21March-AY-Noida-Call-Approva'
        # print('Current login user:', current_user)
        json_result = get_file_name_pattern(server_name, database_name, client_id,user_name,file_name)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/dump_data_into_sentiment', methods=['GET','POST'])
def dump_data_sentiment_table():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    audio_file_name = request.args.get('audio_file')
    if client_id_val and user_name and audio_file_name:
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
        if len(prompt_check_list.open_ai_key) > 0:
            data = sentiment_instance.get_transcribe_data_for_sentiment(server_name, database_name, client_id,user_name,audio_file_name)
            return data
        else:
            data={"message":"Open AI key can't be blank","status":RESOURCE_NOT_FOUND}
            return data,RESOURCE_NOT_FOUND
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/open_ai_transcribe_audio_text', methods=['GET','POST'])
def open_ai_transcribe_audio_text():
    # this end point used only for development
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
    # this end point used only for development
    client_id = int(request.args.get('clientid'))
    audio_file_name = request.args.get('audio_file')
    file = 'D:/Cogent_AI_Audio_Repo/Outbound_DebtDispute/Outbound_DebtDispute.mp3'
    transcript, status  = open_source_transcribe_audio(file)
    if status == SUCCESS:
        data = {"text": transcript,'status': SUCCESS}
        return transcript,status
    return_data = {"text": 'no transcript', 'status': "500"}
    return transcript,status

@app.route('/transcribe_audio_text', methods=['GET','POST'])
def transcribe_audio_text():
    client_id_val = request.args.get('clientid')
    record_id_val = request.args.get('id')
    user_name = request.args.get('username')
    if client_id_val and record_id_val and user_name:
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

        json_result = update_transcribe_audio_text(server_name, database_name, client_id,user_name, record_id)
        return json_result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/token_authenticate', methods=['GET','POST'])
def token_authenticate():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        # print('Current login user:', current_user)
        result = get_token_based_authentication(server_name, database_name, client_id, user_name)
        return result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/ldap_authenticate', methods=['GET','POST'])
def ldap_authenticate():
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
    # current_user = os.getlogin()
    # print('Current login user:', current_user)
    result = get_ldap_authentication(server_name, database_name, client_id)
    return result

@app.route('/update_token', methods=['GET','POST'])
def update_token():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        # print('Current login user:', current_user)
        result = update_authentication_token(server_name, database_name, client_id,user_name)
        return result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/new_token', methods=['GET','POST'])
def new_token():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        # current_user = os.getlogin()
        # print('Current login user:', current_user)
        result = generate_authentication_token(server_name, database_name, client_id,user_name)
        return result
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/sentiment',methods=['GET'])
def sentiment_data():
    return render_template('sentiment_data.html')

@app.route('/transcribe',methods=['GET'])
def merge_transcribe():
    return render_template('merged_chunk_data.html')


@app.route('/get_prohibited_data_from_table', methods=['GET'])
def get_prohibited_data():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        data = sentiment_instance.get_prohibited_data_from_table(server_name, database_name, client_id,user_name)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND

@app.route('/dump_data_into_compliance', methods=['GET','POST'])
def dump_data_compliance_table():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    audio_file_name = request.args.get('audio_file')
    if client_id_val and user_name and audio_file_name:
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
        if len(prompt_check_list.open_ai_key) > 0:
            data = compliance_instance.get_transcribe_data_for_compliance(server_name, database_name, client_id,user_name,audio_file_name)
            return data
        else:
            data={"message":"Open AI key can't be blank","status":RESOURCE_NOT_FOUND}
            return data,RESOURCE_NOT_FOUND
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_data_from_compliance_score', methods=['GET'])
def get_compliance_score_data():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    if client_id_val and user_name:
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
        data = compliance_instance.get_data_from_compliance_score(server_name, database_name, client_id,user_name)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/get_data_from_compliance_table', methods=['GET'])
def get_compliance_data():
    client_id_val = request.args.get('clientid')
    user_name = request.args.get('username')
    audio_file_name = request.args.get('audio_file')
    if client_id_val and user_name and audio_file_name:
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
        data = compliance_instance.get_compliance_data_from_table(server_name, database_name, client_id,user_name,audio_file_name)
        return data
    else:
        response_message = 'The api does not send you all of the necessary parameters. Please give it another go using every parameter.'
        return {
            "result": [response_message],
            "message": response_message,
            "status": 'failed',
            'status_code': RESOURCE_NOT_FOUND
        }, RESOURCE_NOT_FOUND


@app.route('/compliance',methods=['GET'])
def compliance_data():
    return render_template('compliance.html')


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
