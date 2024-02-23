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

# https://loguru.readthedocs.io/en/stable/api/logger.html

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

################################################################

# logger.add("file.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
################################################################
# logger.add(sys.stdout, format="{time} - {level} - {message}", filter="sub.module")
################################################################
# logger.add("file_{time}.log", level="TRACE", rotation="100 MB")
################################################################
# def debug_only(record):
#     return record["level"].name == "DEBUG"

# logger.add("debug.log", filter=debug_only)
################################################################

# def my_sink(message):
#     record = message.record
#     # update_db(message, time=record["time"], level=record["level"])

# logger.add(my_sink)

################################################################
# level_per_module = {
#     "": "DEBUG",
#     "third.lib": "WARNING",
#     "anotherlib": False
# }
# logger.add(lambda m: print(m, end=""), filter=level_per_module, level=0)
################################################################
from loguru import logger
################################################################

# async def publish(message):
#             await api.post(message)

# logger.add(publish, serialize=True)
################################################################

# from logging import StreamHandler
# logger.add(StreamHandler(sys.stderr), format="{message}")

################################################################

# class RandomStream:
#     def __init__(self, seed, threshold):
#         self.threshold = threshold
#         random.seed(seed)
#     def write(self, message):
#         if random.random() > self.threshold:
#             print(message)

# stream_object = RandomStream(seed=12345, threshold=0.25)
# logger.add(stream_object, level="INFO")

################################################################

# i = logger.add(sys.stderr, format="{message}")
# logger.info("Logging")
# logger.remove(i)
# logger.info("No longer logging")
################################################################
# def process():
#     logger.info("Message sent from the child")
#     logger.complete()

# logger.add(sys.stderr, enqueue=True)

# process = multiprocessing.Process(target=process)
# process.start()
# process.join()

################################################################
# decorator / context manager
# @logger.catch
# def f(x):
#     100 / x

# def g():
#     f(10)
#     f(0)
# g()
################################################################
# with logger.catch(message="Start the Gen AI "):
#       main()  # No exception, no logs
################################################################


################################################################


################################################################


################################################################


################################################################


################################################################
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
