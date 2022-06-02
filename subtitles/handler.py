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

import pysubs2
from . import reader
import tempfile
import vlc
import logging
from misc import utils
import os
import wx
from gui import dialogs
from cytolk.tolk import speak
from datetime import timedelta


class SubHandler:
    def __init__(self, parent):
        self.panel = parent
        # The delaying period for speaking subtitles(In milliseconds.)
        self.delay_by = 0
        self.index = 0
        self.queue = []
        self.queue_index = 0
        self.subtitle_handler = None
        # The list of subtitles, A dictionary with keys of value string, For the name, And values for the
        # value tuple (Default, subtitle_path)
        self.subtitles = {}
        self.subtitle_text = ""
        # The current subtitle file selected.
        self.subtitle = ""
        self.processed_events = []
        # Temporary directory, For storing extracted subtitles from media, If any.
        self.temp_dir = None

    def update(self):
        if not self.subtitle_handler or self.index >= len(self.subtitle_handler) - 1:
            return
        if (
            utils.get_subtitle_tuple(self.subtitle_handler[self.index])
            in self.processed_events
        ):
            self.check_for_subtitle()
            return
        start = timedelta(
            milliseconds=self.subtitle_handler.events[self.index].start + self.delay_by
        )
        end = timedelta(
            milliseconds = self.subtitle_handler[self.index].end + self.delay_by
        )
        current = timedelta(seconds = self.panel.media.player.time_pos)
        if current >= start and current <= end:
            self.queue.append(self.subtitle_handler[self.index].plaintext)
            self.processed_events.append(
                utils.get_subtitle_tuple(self.subtitle_handler[self.index])
            )
            self.index += 1
            return
        self.check_for_subtitle()

    def check_for_subtitle(self):
        for (val, i) in enumerate(self.subtitle_handler):
            if utils.get_subtitle_tuple(i) in self.processed_events:
                continue
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(seconds = self.panel.media.player.time_pos)
            if current >= start and current <= end:
                self.queue.append(i.plaintext)
                self.processed_events.append(utils.get_subtitle_tuple(i))
                self.index = val
                break

    def on_queue(self):
        if len(self.queue) == 0 or self.queue_index > len(self.queue) - 1:
            return
        text = self.queue[self.queue_index].replace(r"\N", "\n")
        if text == "":
            self.queue.remove(self.queue[self.queue_index])
            return
        speak(text)
        self.queue.remove(self.queue[self.queue_index])

    def stringify_subtitles(self):
        final_list = []
        for i in self.subtitles:
            final_list.append(i)
        return final_list

    def destroy(self):
        self.subtitle_handler = None
        self.subtitles.clear()
        self.subtitle = ""
        self.queue_reset()
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None


    def load(self, dir, file):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.subtitles = reader.generate_subtitles(
            os.path.join(dir, file), self.temp_dir
        )
        for (i, j) in self.subtitles.values():
            if i == 1:
                self.subtitle = j
                break
        if len(self.subtitles) > 0 and self.subtitle == "":
            for (i, val) in self.subtitles.values():
                self.subtitle = val
                break
        external_subs = utils.check_for_similar_subtitles(dir, file)
        if len(external_subs) > 0:
            self.subtitles.update(external_subs)
            self.subtitle = next(iter(external_subs.items()))[1][1]
        if self.subtitles:
            self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")


    def delay_set(self):
        with dialogs.SubDelay(
            self, "Define subtitle delay(In milliseconds)", value=str(self.delay_by)
        ) as dlg:
            r = dlg.ShowModal()
            if r == wx.ID_OK:
                val = dlg.intctrl.GetValue()
                self.delay_by = int(val)
                self.panel.media.player.sub_delay = int(val)
                speak(f"Subtitle delay set to {self.delay_by}", True)

    def subtitle_select(self, event=None):
        if len(self.subtitles) == 0 or not self.subtitle_handler:
            return
        with dialogs.SubtitleSelect(self) as dlg:
            r = dlg.ShowModal()
            if r != wx.ID_OK:
                return
            sub = dlg.subtitle_select.GetString(dlg.subtitle_select.Selection)
            if not sub:
                wx.MessageBox(
                    "Aborting...",
                    "No subtitle selected",
                    wx.ICON_ERROR,
                )
                return
            if sub not in self.subtitles:
                wx.MessageBox(
                    "There was an error while trying to parse the selected subtitle... Please try again later.",
                    "Fatal error",
                    wx.ICON_ERROR,
                )
                return
            self.subtitle = self.subtitles[sub][1]
            self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")

    def queue_reset(self):
        if (
            not self.subtitle_handler
            or len(self.subtitles) == 0
            or len(self.subtitle_handler) == 0
        ):
            return
        self.queue.clear()
        self.queue_index = 0
        self.index = 0
        self.processed_events.clear()
        for (val, i) in enumerate(self.subtitle_handler):
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(seconds = self.panel.media.player.time_pos)
            if current >= start and current <= end:
                self.queue.append(i.plaintext)
                self.processed_events.append(utils.get_subtitle_tuple(i))
                self.index = val


    def doLoadSubtitle(self, file, dir):
        try:
            self.subtitle_handler = pysubs2.load(
                os.path.join(dir, file), encoding="utf-8"
            )
        except Exception:
            logging.error("Could not load subtitles", exc_info=True)
            wx.MessageBox(
                "That file couldn't be loaded. Make sure it's a supported format and try again.",
                "File couldn't be loaded",
                wx.ICON_ERROR,
            )
            return
        self.subtitles[file] = (0, os.path.join(dir, file))
