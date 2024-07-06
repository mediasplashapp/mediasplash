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
from gui import messageBox
from . import reader
from . import classes
import tempfile
import logging
from misc import utils
import os
import wx
from gui import dialogs
from speech import speak
from datetime import timedelta


class SubHandler:
    def __init__(self, parent):
        self.panel = parent
        # the prefered subtitle, usually the one last selected.
        self.last_subtitle = None
        # The delaying period for speaking subtitles(In milliseconds.)
        self.delay_by = 0
        self.index = 0
        self.subtitle_handler = None
        # The list of subtitles, A dictionary with keys of value string, For the name, And values for the
        # value tuple (Default, subtitle_path)
        self.subtitles = []
        self.subtitle_text = ""
        # The current subtitle file selected.
        self.subtitle = ""
        self.processed_events = []
        # Temporary directory, For storing extracted subtitles from media, If any.
        self.temp_dir = None

    def update(self):
        if not self.subtitle_handler or self.index > len(self.subtitle_handler) - 1:
            return
        if utils.get_subtitle_tuple(self.subtitle_handler[self.index]) in self.processed_events:
            self.check_for_subtitle()
            return
        start = timedelta(milliseconds=self.subtitle_handler.events[self.index].start + self.delay_by)
        end = timedelta(milliseconds=self.subtitle_handler[self.index].end + self.delay_by)
        current = timedelta(seconds=self.panel.media.player.time_pos)
        if current >= start and current <= end:
            self.speak_sub(self.subtitle_handler[self.index].plaintext)
            self.processed_events.append(utils.get_subtitle_tuple(self.subtitle_handler[self.index]))
            self.index += 1
            return
        self.check_for_subtitle()

    def check_for_subtitle(self):
        for val, i in enumerate(self.subtitle_handler):
            if utils.get_subtitle_tuple(i) in self.processed_events:
                continue
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(seconds=self.panel.media.player.time_pos)
            if current >= start and current <= end:
                self.speak_sub(i.plaintext)
                self.processed_events.append(utils.get_subtitle_tuple(i))
                self.index = val
                break

    def speak_sub(self, text):
        text = text.replace(r"\N", "\n")
        if text == "":
            return
        speak(text, False)

    def stringify_subtitles(self):
        final_list = []
        for i in self.subtitles:
            final_list.append((i.title if i.title else i.language))
        return final_list

    def destroy(self):
        self.subtitle_handler = None
        self.subtitles.clear()
        self.subtitle = ""
        self.reset()
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None

    def load(self, dir, file):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.subtitles = reader.generate_subtitles(os.path.join(dir, file), self.temp_dir)
        for i in self.subtitles:
            if i.default == 1:
                self.subtitle = i.path
                break
        if len(self.subtitles) > 0 and self.subtitle == "":
            self.subtitle = self.subtitles[0].path
        external_subs = utils.check_for_similar_subtitles(dir, file)
        if len(external_subs) > 0:
            self.subtitles.extend(external_subs)
            self.subtitle = self.subtitles[0].path
        if self.subtitles:
            self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")

    def delay_set(self):
        with dialogs.SubDelay(self, "Define subtitle delay(In milliseconds)", value=str(self.delay_by)) as dlg:
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
                messageBox(
                    self.panel,
                    "Aborting...",
                    "No subtitle selected",
                    wx.ICON_ERROR,
                )
                return
            self.set_subtitle(sub, by_default = True)

    def set_subtitle(self, sub, by_default = False):
            for i in self.subtitles:
                if i.title and i.title == sub or i.language and i.language == sub:
                    if by_default:
                        self.last_subtitle = i.title if i.title else i.language
                    self.subtitle = i.path
                    break
            subs = utils.generate_track_info(self.panel.media.player.track_list, "subtitle")
            for val, i in enumerate(subs):
                if i == sub:
                    self.panel.media.player.sub = val + 1
                    break
            if os.path.exists(self.subtitle):
                self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")

    def reset(self):
        if not self.subtitle_handler or len(self.subtitles) == 0 or len(self.subtitle_handler) == 0:
            return
        self.index = 0
        self.processed_events.clear()
        for val, i in enumerate(self.subtitle_handler):
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(seconds=self.panel.media.player.time_pos)
            if current >= start and current <= end:
                self.speak_sub(i.plaintext)
                self.processed_events.append(utils.get_subtitle_tuple(i))
                self.index = val

    def doLoadSubtitle(self, dir, file):
        try:
            self.subtitle_handler = pysubs2.load(os.path.join(dir, file), encoding="utf-8")
            self.panel.media.player.sub_add(os.path.join(dir, file))
        except Exception:
            logging.error("Could not load subtitles", exc_info=True)
            messageBox(
                self.panel,
                "That file couldn't be loaded. Make sure it's a supported format and try again.",
                "File couldn't be loaded",
                wx.ICON_ERROR,
            )
            return
        self.subtitles.append(classes.Subtitle(title=file, external=True, path=os.path.join(dir, file)))
