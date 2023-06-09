# observer manager
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.

import wx
import global_vars
from speech import speak
import logging


class ObserverManager:
    def __init__(self, media):
        self.media = media

    def chapter_observer(self, name, value):
        metadata = self.media.player.chapter_metadata
        title = metadata.get("TITLE") if metadata else None
        if title:
            speak(title, True)
            wx.CallAfter(self.media.panel.frame.SetTitle, f"{title} - {self.media.title} - {global_vars.info.name}")

    def register_observers(self):
        self.media.player.observe_property("chapter", self.chapter_observer)
