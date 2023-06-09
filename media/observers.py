# observer manager
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.


import mpv
from speech import speak
import logging


class ObserverManager:
    def __init__(self, player: mpv.MPV):
        self.player = player

    def chapter_observer(self, name, value):
        metadata = self.player.chapter_metadata
        if metadata and metadata.get("TITLE"):
            speak(metadata.get("TITLE"), True)

    def register_observers(self):
        self.player.observe_property("chapter", self.chapter_observer)
