from flask import Flask, request, jsonify
app = Flask(__name__)

from database_query_utils import *
from database_query_utils import DBRecord
db_instance = DBRecord()

@app.route('/get_all_data', methods=['GET'])
def get_record():
    table_name = request.args.get('table_name')
    data = db_instance.get_all_record(table_name)
    if data ==None:
        data={"Error":"Invalid table/Data not available for this "+ table_name}
    return data

@app.route('/get_record_by_id', methods=['GET'])
def get_recordby_id():
    table_name = request.args.get('table_name')
    id = request.args.get('id')
    data = db_instance.get_record_by_id(table_name,id)
    if data == None:
        data={"Error":"Invalid table/Data not available for this "+ table_name}
    return data

@app.route('/get_record_by_column_name', methods=['GET'])
def get_recordby_column_name():

    table_name = request.args.get('table_name')
    column_name = request.args.get('column_name')
    column_value = request.args.get('column_value')

    data = db_instance.get_data_by_column_name(table_name,column_name,column_value)

    if data == None:
        data={"Error":"Invalid table/Data not available for this "+ table_name}
    return data


@app.route('/update_record_by_column', methods=['GET'])
def get_update_by_column_name():

    table_name = request.args.get('table_name')
    column_to_update = request.args.get('column_to_update')
    new_value = request.args.get('new_value')
    condition_column = request.args.get('condition_column')
    condition_value = request.args.get('condition_value')

    data = db_instance.update_record_by_column(table_name,column_to_update,new_value,condition_column,condition_value)

    if data == None:
        data={"Error":"Invalid table/Data not available for this "+ table_name}
    return data

@app.route('/delete_record_by_id')
def delete_recordby_id():

    table_name = request.args.get('table_name')
    itm_id = request.args.get('id')
    data = db_instance.delete_record_by_id(table_name,itm_id)

    if data == None:
        data={"Error":"Invalid table/Data not available for this "+ table_name}
    return {'data': data}

@app.route('/get_data_from_transcribe_tracker_table')
def get_transcribe_sentiment():
    from app.model.sentiment_analysis import SentimentAnalysisCreation
    sentiment_instance = SentimentAnalysisCreation()
    transcribe_id = request.args.get('transcribe_id')
    sentiment_check = request.args.get('sentiment_check')
    data = sentiment_instance.get_data_from_transcribe_tracker_table(transcribe_id,sentiment_check)
    if data == None:
        data={"Error":"Invalid table/Data not available for this "+ sentiment_check}
    return {'data': data}

if __name__ == '__main__':
    app.run(debug=True)
