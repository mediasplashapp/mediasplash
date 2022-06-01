"""
    mediasplash, A simple media player with screen reader subtitle support.
    Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
os.add_dll_directory(os.getcwd())

import mpv
from misc import utils
from functools import cached_property


supported_media = (
    ".mp3",
    ".mp4",
    ".mkv",
    ".ogg",
    ".opus",
    ".wav",
    ".aac",
    ".m4a",
    ".flac",
)


class Media:
    def __init__(self, parent):
        self.panel = parent
        self.dir = ""
        self.file = ""
        self.state = utils.MediaState.neverPlayed
        self.player: mpv.MPV = mpv.MPV(wid = self.panel.GetHandle())
        #self.player.set_hwnd(self.panel.GetHandle())

    #def update(self):
    #    if self.player.get_state() == vlc.State.Ended:
    #        self.onStop()

    def load(self, dir, file):
        self.dir = dir
        self.file = file
        self.player.play(os.path.join(dir, file))
        self.player.wait_until_playing()
        if hasattr(self.__dict__, "length"):
            del self.__dict__["length"]

    @cached_property
    def length(self):
        return self.player.duration

    def next_file(self):
        if not self.dir or not self.file:
            return
        files = os.listdir(self.dir)
        if self.file not in files:
            return
        file_index = files.index(self.file)
        for i in files[file_index:]:
            if not i == self.file and os.path.splitext(i)[1] in supported_media:
                self.panel.doLoadFile(i, self.dir)
                break

    def previous_file(self):
        if not self.dir or not self.file:
            return
        files = os.listdir(self.dir)
        if self.file not in files:
            return
        file_index = files.index(self.file)
        for i in reversed(files[:file_index]):
            if not i == self.file and os.path.splitext(i)[1] in supported_media:
                self.panel.doLoadFile(i, self.dir)
                break

    def onPlay(self):
        self.player.pause = False
        if self.state != utils.MediaState.playing:
            self.state = utils.MediaState.playing

    def onPause(self):
        self.player.pause = True
        if self.state != utils.MediaState.paused:
            self.state = utils.MediaState.paused

    def onStop(self):
        self.panel.subtitles.queue_reset()
        self.player.stop()
