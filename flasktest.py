from flask import Flask, request, jsonify,json
from alchemy_encoder import AlchemyEncoder
app = Flask(__name__)

from database_query_utils import *
from database_query_utils import DBRecord
from flack_service import FlaskDBService

db_instance = DBRecord()
database_service = FlaskDBService()
server_name = 'FLM-VM-COGAIDEV'
database_name = 'AudioTrans'


@app.route('/get_all_data', methods=['GET'])
def get_record():
    table_name = request.args.get('table_name')
    data = db_instance.get_all_record(table_name)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/get_record_by_id', methods=['GET'])
def get_recordby_id():
    table_name = request.args.get('table_name')
    id = request.args.get('id')
    data = db_instance.get_record_by_id(table_name, id)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/get_record_by_column_name', methods=['GET'])
def get_recordby_column_name():
    table_name = request.args.get('table_name')
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')

    data = db_instance.get_data_by_column_name(table_name, column_name, column_value)

    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/update_record_by_column', methods=['GET'])
def get_update_by_column_name():
    table_name = request.args.get('table_name')
    column_to_update = request.args.get('column_to_update')
    new_value = request.args.get('new_value')
    condition_column = request.args.get('condition_column')
    condition_value = request.args.get('condition_value')

    data = db_instance.update_record_by_column(table_name, column_to_update, new_value, condition_column,
                                               condition_value)

    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return data


@app.route('/delete_record_by_id')
def delete_recordby_id():
    table_name = request.args.get('table_name')
    itm_id = request.args.get('id')
    data = db_instance.delete_record_by_id(table_name, itm_id)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    return {'data': data}


@app.route('/get_audio_transcribe_data', methods=['GET'])
def get_audio_transcribe_data():
    client_id = int(request.args.get('clientid'))
    table_name = 'AudioTranscribe'
    # data = db_instance.get_master_data_by_id(table_name, int(client_id))
    data = database_service.get_audio_transcribe_table_data(server_name,database_name,client_id)
    if data == None:
        data = {"Error": "Invalid table/Data not available for this " + table_name}
    data_json = json.dumps(data, cls=AlchemyEncoder)
    return {'data': data_json}


if __name__ == '__main__':
    app.run(debug=True)
