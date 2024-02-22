from loguru import logger
import whisper 
import openai
from pydub import AudioSegment
import subprocess
import shutil
import os
from datetime import datetime
import time
from openai import OpenAI
import speech_recognition as sr



# logger.debug("Happy logging with Loguru!")
# logger.trace("A trace message.")
# logger.debug("A debug message.")
# logger.info("An info message.")
# logger.success("A success message.")
# logger.warning("A warning message.")
# logger.error("An error message.")
# logger.critical("A critical message.")

import sys

# logger.level("FATAL", no=60, color="<red>", icon="!!!")
# logger.log("FATAL", "A user updated some information.")
# class Logger(logger):      
#     def __init__(self, logger):
#         self.logger = logger
# it corresponds to the maximum number of bytes the current file is allowed to hold before a new one is created
# logger.add("loguru.log", rotation="5 seconds")
# logger.debug("A debug message.")


# def load_model():
#     try:
#         model = whisper.load_model("tiny-3")
#         result = model.transcribe("D:/Cogent_Audio_Repo/Interview1.mp3")
#         return result
#     except Exception as e:
#             lgger.log()
#             logger.critical("A critical message.",e)
#     # print(result)
#     # with open("D:/Cogent_Audio_Repo/Interview1.txt","w") as f:
#     #     f.write(result["text"])

# print('model load run',load_model())


from loguru import logger

class LoggerMixin:
    def __init__(self):
        self.logger = logger.bind(classname=self.__class__.__name__)

class Hello(LoggerMixin):
    def __init__(self):
        super().__init__()

    def world(self):
        self.logger.info("hello world")

fmt = "{extra[classname]}:{function}:{line} - {message}"
logger.remove()  # Remove default handler
logger.add(sys.stderr, format=fmt)

Hello().world();
