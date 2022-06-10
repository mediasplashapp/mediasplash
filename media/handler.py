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
import logging

os.add_dll_directory(os.getcwd())

import mpv
from misc import utils
from functools import cached_property
import concurrent.futures
from gui import messageBox
import wx

def log_handler(level, prefix, message):
    message = message.strip()
    prefix = prefix.strip()
    if not message or not prefix:
        return
    message = f"{prefix} {message}"
    if level == "fatal" or level == "error":
        level = 40
    elif level == "warn":
        level = 30
    elif level == "info":
        level = 20
    elif level == "v" or level == "trace" or level == "debug":
        level = 10
    else:
        logging.debug(f"{level} {message}")
        return
    logging.log(level, message)


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
        self.is_url = False
        self.state = utils.MediaState.neverPlayed
        self.player: mpv.MPV = mpv.MPV(
            wid=self.panel.GetHandle(),
            hwdec="d3d11va-copy",
            profile="libmpv",
            cache=True,
            demuxer_max_bytes="300MiB",
            demuxer_readahead_secs=30,
            load_scripts=False,
            log_handler=log_handler,
            loglevel="info",
            ytdl = True,
        )

    def load(self, dir, file, url = False):
        self.dir = dir
        self.file = file
        self.is_url = url
        if url:
            self.player.play(file)
        else:
            self.player.play(os.path.join(dir, file))
        try:
            self.player.wait_until_playing(10.0)
        except concurrent.futures._base.TimeoutError:
            messageBox(
                self.panel,
                "The media loading have timed out, Please make sure that this media file is valid and try again.",
                "Error",
                wx.ICON_ERROR,
            )
        if hasattr(self.__dict__, "length"):
            del self.__dict__["length"]

    @cached_property
    def length(self):
        return self.player.duration

    def find_device(self, device):
        devices = self.player.audio_device_list
        for i in devices:
            if i["name"] == device:
                return i["description"]

    def next_chapter(self):
        if self.player.chapter == self.player.chapters:
            return
        self.player.chapter = self.player.chapter + 1

    def previous_chapter(self):
        if self.player.chapter == 1:
            return
        self.player.chapter = self.player.chapter - 1

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
        self.panel.subtitles.reset()
        self.player.stop()
