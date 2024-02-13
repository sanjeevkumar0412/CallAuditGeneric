from pydub import AudioSegment

# Load the audio file
audio = AudioSegment.from_file("audio_1.mp3")
#print("pydub >>>>>>>>>.",len(audio))
# Define the duration of each chunk (in milliseconds)
chunk_length_ms = 10000  # 10 seconds

# Split the audio into chunks
chunks = []
audio_fi="audio_1.mp3"

import os
import openai
import whisper
import warnings
warnings.simplefilter("ignore")
from openai import OpenAI
os.environ["OPENAI_API_KEY"] = ""
client = OpenAI()
ffmpeg_path = 'C:/ffmpeg/ffmpeg-master-latest-win64-gpl/bin'
os.environ['PATH'] = f'{ffmpeg_path};{os.environ["PATH"]}'

model = whisper.load_model("base")

from pydub import AudioSegment
from pydub.silence import split_on_silence
# whisper.DecodingOptions
import time
second_check=time.localtime().tm_sec
def chunk_audio(audio):
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        result = model.transcribe(chunk)
        chunks.append(chunk)   
    return chunks
#print("chunk_audio >>>>>>>>.",chunk_audio(audio_fi))

import speech_recognition as sr
from pydub import AudioSegment

# Function to split audio into chunks
def split_audio_into_chunks(audio_file_path, chunk_length_ms):
    audio = AudioSegment.from_file(audio_file_path)
    return [audio[i:i+chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

# Function to transcribe audio chunk
def transcribe_chunk(chunk):
    recognizer = sr.Recognizer()
    with sr.AudioData(chunk.raw_data, chunk.frame_rate, chunk.sample_width) as audio_data:
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "[Unrecognized]"
        except sr.RequestError as e:
            text = "[Error: {}]".format(e)
    return text

# Example usage:
audio_file_path = audio
# chunk_length_ms = 5000  # 5 seconds
# chunks = split_audio_into_chunks(audio_file_path, chunk_length_ms)



transcriptions = []
for chunk in chunks:
    transcription = transcribe_chunk(chunk)
    transcriptions.append(transcription)

# print(transcriptions)

def whisper_method(audio):
    trans = model.transcribe(audio)
    result=trans["text"]
    return result

# print("Execution TIme ",second_check,"Whisper >>>>.",whisper_method(audio_fi))

def open_ai(audio):
    audio_file= open(audio,"rb")
    trans = client.audio.translations.create(model="whisper-1", file=audio_file,response_format="text")
    return trans
# print("Execution TIme ",second_check,"OpenAI >>>>.",open_ai(audio_fi))
#
# def split_audio(path):
#     sound = AudioSegment.from_file(path)
#     chunks = split_on_silence(sound,
#     min_silence_len=1500,
#     silence_thresh=sound.dBFS - 14,
#     keep_silence=1500,
#     )
# import json
def chunk_large_audio_file(path):
    sound = AudioSegment.from_file(path)
    chunks = split_on_silence(sound,
        min_silence_len = 1500,
        silence_thresh = sound.dBFS-14,
        keep_silence=1500,
    )
    # split_audio(path)
    folder_name = path.split('.')[0]

    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # Condition need to apply here.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.mp3")
        audio_chunk.export(chunk_filename, format="mp3")
        try:
            text = whisper_method(chunk_filename)
            print("SPlit Recording>>>>",text)
        except Exception as e:
            # print("Error:", str(e))
            # print(e)
            pass
        else:
            text = f"{text.capitalize()}."
            # print(chunk_filename, ":", text)
            whole_text += text
    with open(folder_name+"_audio_file", "w") as f:
        f.write(whole_text)
        # json_data = json.load(f)
    return whole_text

# print("Execution TIme ",second_check,"Split File >>>>.",chunk_large_audio_file(audio_fi))



