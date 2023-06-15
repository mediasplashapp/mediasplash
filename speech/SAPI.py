import platform
from . import SAPI5
from . import NSSS
class tts_voice(object):
    def __init__(self):
#Initializes the Steel TTS library to use the SAPI5 engine.

        if platform.system()=="Darwin":
            self.engine=NSSS.NSSS()
        else:
            self.engine=SAPI5.SAPI5()

    def get_voices(self):
        return self.engine.available_voices()

    def set_rate(self, rate):
#set the tts rate
        self.engine.set("rate",rate)

    def get_rate(self):
#get the tts rate
        return self.engine.get("rate")

    rate= property(get_rate, set_rate)

    def set_pitch(self, pitch):
#set the tts pitch
        self.engine.set("pitch",pitch)

    def get_pitch(self):
#get the tts pitch
        return self.engine.get("pitch")

    pitch= property(get_pitch, set_pitch)

    def set_volume(self, volume):
#set the tts volume
        self.engine.set("volume",volume)

    def get_volume(self):
#get the tts volume
        return self.engine.get("volume")

    volume= property(get_volume, set_volume)

    def set_voice(self,voice):
        self.engine.set('voice',voice)

    def stop(self):
        self.engine.stop()

    def speak(self,text,interrupt=False):
#Make the TTS voice speak. Interrupt will make the tts voice stop speaking before the next string starts.

        if interrupt==True:
            self.engine.stop()

        self.engine.speak(text)