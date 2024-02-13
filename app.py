from utils import *
from flask import Flask,jsonify
app = Flask(__name__)

audio_fi = "audio_1.mp3"

@app.route('/GetWhisperJson',methods=['GET'])
# @app.route('/GetWhisperJson/<path>',methods=['GET'])
def GetWhisperJson():
    split_audio_file = chunk_large_audio_file(audio_fi)
    print("Execution TIme>>>>. ",second_check,"Split Audio File >>>>.",split_audio_file)
    datacreation = jsonify({'data': split_audio_file})
    data = datacreation.data
    return data

if __name__ == '__main__':
    app.run()