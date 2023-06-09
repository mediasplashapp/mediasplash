# speech
# Copyright (C) 2023 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


from cytolk import tolk

global initialized
initialized = False


def speak(text: str, interrupt: bool = False):
    if not initialized:
        tolk.load()
    tolk.speak(text, interrupt)


def speech_terminate():
    tolk.unload()
    initialized = False
