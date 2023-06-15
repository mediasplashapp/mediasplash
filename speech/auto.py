#Allows for you to speak text through your default screen reader.
import sys
import subprocess
import os
import platform
from . import SAPI
last_spoken=""
if platform.system()=="Darwin": v=SAPI.tts_voice()
if platform.system()=="Windows":
	import cytolk
	from cytolk import tolk
	tolk.try_sapi(True)
	if not tolk.is_loaded():
		tolk.load("__compiled__" not in globals())
if platform.system()=="Linux":
	import speechd
	s=speechd.Speaker("mediasplash")

def speak(text,interrupt=True):
    global last_spoken
    last_spoken=text
    #speaker = outputs.auto.Auto()
    if platform.system()=="Darwin":
        v.speak(text,interrupt)
    elif platform.system()=="Windows":
        tolk.speak(text,interrupt)
    else:
        if interrupt: s.cancel()
        s.speak(text)

def speech_terminate():
    if platform.system() == "Windows":
        tolk.unload()
