# Allows for you to speak text through your default screen reader.
import platform

last_spoken = ""
loaded = False
if platform.system() == "Darwin":
    from . import NSSS
    v = NSSS.NSSS()
if platform.system() == "Windows":
    from cytolk import tolk
if platform.system() == "Linux":
    import speechd

    s = speechd.Speaker("mediasplash")


def speak(text, interrupt=True):
    global last_spoken
    global loaded
    last_spoken = text
    if platform.system() == "Darwin":
        v.speak(text, interrupt)
    elif platform.system() == "Windows":
        if not loaded:
            tolk.load("__compiled__" not in globals())
            loaded = True
        tolk.speak(text, interrupt)
    else:
        if interrupt:
            s.cancel()
        s.speak(text)


def speech_terminate():
    if platform.system() == "Windows":
        tolk.unload()
