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

import sys
import os
import math
from data_manager import DataManager as dm
from gui import dialogs, messageBox
from gui.goto import GoToDialog
from global_vars import info
from datetime import timedelta
import webbrowser
import logging
from misc import utils, update_check
from gui import custom_controls
import platform
import traceback
import wx
from speech import speak, speech_terminate

from gui.media_panel import MediaPanel


class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title=info.name)
        self.mpanel = MediaPanel(self)
        self.app = app
        self.mpanel.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.Centre()
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.fileStream = self.fileMenu.Append(wx.ID_ANY, "Open from URL...\tAlt+u")
        self.subtitleOpen = self.fileMenu.Append(wx.ID_ANY, "Open subtitle...\tAlt+O")
        self.exit_item = self.fileMenu.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self.menubar.Append(self.fileMenu, "&file")
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.mediaMenu = wx.Menu()
        self.subtitleSelectMenu = self.mediaMenu.Append(wx.ID_ANY, "Change subtitle.\tAlt+C")
        self.subDelay = self.mediaMenu.Append(wx.ID_ANY, "Change subtitle delay...\tAlt+D")
        self.jumpItem = self.mediaMenu.Append(wx.ID_ANY, "Jump to...\tctrl+J")
        self.audio_tracks_menu = custom_controls.ClearableMenu()
        self.mediaMenu.AppendSubMenu(self.audio_tracks_menu, "Audio tracks")
        self.audio_devices_menu = custom_controls.ClearableMenu()
        self.mediaMenu.AppendSubMenu(self.audio_devices_menu, "Audio output device")
        self.menubar.Append(self.mediaMenu, "&Media")
        self.helpMenu = wx.Menu()
        self.updateCheck = self.helpMenu.Append(wx.ID_ANY, "Check for updates...")
        self.fileAbout = self.helpMenu.Append(wx.ID_ABOUT)
        self.menubar.Append(self.helpMenu, "&Help")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadUrl, self.fileStream)
        self.Bind(wx.EVT_MENU, self.about, self.fileAbout)
        self.Bind(wx.EVT_MENU, self.onUpdateCheck, self.updateCheck)
        self.Bind(wx.EVT_MENU, self.mpanel.subtitles.subtitle_select, self.subtitleSelectMenu)
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, self.subtitleOpen)
        self.Bind(wx.EVT_MENU, lambda event: self.mpanel.subtitles.delay_set(), self.subDelay)
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), self.exit_item)
        self.Bind(wx.EVT_MENU, self.on_jump, self.jumpItem)
        self.audio_tracks_menu.Bind(wx.EVT_MENU, self.audio_track_set)
        self.audio_devices_menu.Bind(wx.EVT_MENU, self.audio_device_set)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.mpanel.audio_devices_set()
        self.data = dm(os.path.join(info.data_path, "config.json"))
        self.load()

    def about(self, event):
        with dialogs.AboutDialog(self) as dlg:
            dlg.ShowModal()

    def onUpdateCheck(self, event):
        updateData = update_check.check()
        if updateData:
            if (
                messageBox(
                    self,
                    f"A new update of {info.name} is available. New version: {'.'.join(updateData)}. Download the update now?",
                    "Update available",
                    wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING,
                )
                == wx.ID_YES
            ):
                webbrowser.open_new(
                    "https://github.com/mediasplashapp/mediasplash/releases/latest/download/mediasplash.zip"
                )
            return
        messageBox(self, "No update found", "No updates", wx.ICON_WARNING)

    def on_jump(self, event):
        chapters = self.mpanel.media.player.chapter_list
        cur_chapter = self.mpanel.media.player.chapter
        logging.debug(chapters)
        with GoToDialog(self, chapters) as dlg:
            if chapters:
                chapters_page = dlg.book.GetPage(1)
                chapters_page.list_ctrl.Focus(cur_chapter)
                chapters_page.list_ctrl.Select(cur_chapter)
            position_page = dlg.book.GetPage(0)
            position_page.text.SetValue(str(timedelta(seconds=round(self.mpanel.media.player.time_pos))).replace(":", "."))
            position_page.text.SelectAll()

            if dlg.ShowModal() == wx.ID_OK:
                delta = None

                def show_error():
                    messageBox(self, "input is not valid", "Error", wx.ICON_ERROR)

                value = dlg.dlg_value
                if dlg.selection == 1 and value != -1:
                    self.mpanel.media.player.chapter = value
                    self.mpanel.subtitles.reset()
                    return
                val = value.split(".")
                if val[0] == value:
                    val = value.split(":")
                value = val
                value = [int(v) for v in value if v.isdigit()]
                if not value:
                    show_error()
                    return
                if len(value) == 2:
                    delta = timedelta(minutes=value[0], seconds=value[1])
                elif len(value) == 1:
                    delta = timedelta(seconds=value[0])
                elif len(value) == 3:
                    delta = timedelta(hours=value[0], minutes=value[1], seconds=value[2])
                elif len(value) == 4:
                    delta = timedelta(
                        days=value[0],
                        hours=value[1],
                        minutes=value[2],
                        seconds=value[3],
                    )

                else:
                    show_error()
                    return
                total = delta.total_seconds() if delta is not None else None
                if total is None or total > self.mpanel.media.length or total < 0:
                    show_error()
                    return
                self.mpanel.media.player.time_pos = total
                self.mpanel.subtitles.reset()

    def audio_device_set(self, event):
        result = self.audio_devices_menu.GetChecked().GetItemLabelText()
        devices = self.mpanel.media.player.audio_device_list
        for i in devices:
            if i["description"] == result:
                self.mpanel.media.player.audio_device = i["name"]

    def audio_track_set(self, event):
        result = self.audio_tracks_menu.GetChecked().GetItemLabelText()
        self.mpanel.media.last_audio_track = result
        self.set_audio_track(result)

    def set_audio_track(self, track):
        tracks = utils.generate_track_info(self.mpanel.media.player.track_list, "audio")
        for val, i in enumerate(tracks):
            if i == track:
                for i in self.audio_tracks_menu.MenuItems:
                    if i.ItemLabelText == track:
                        i.Check()
                self.mpanel.media.player.aid = val + 1
                return True
        return False

    def load(self):
        self.data.load()
        if self.data.exists("last_audio_track"):
            self.mpanel.media.last_audio_track = self.data.get("last_audio_track")
        if self.data.exists("last_subtitle"):
            self.mpanel.subtitles.last_subtitle = self.data.get("last_subtitle")
        if self.data.exists("subtitle_delay"):
            self.mpanel.subtitles.delay_by = int(self.data.get("subtitle_delay"))
            self.mpanel.media.player.sub_delay = int(self.data.get("subtitle_delay"))
        if self.data.exists("volume"):
            self.mpanel.media.player.volume = int(self.data.get("volume"))
        if self.data.exists("saved_track"):
            tup = self.data.get("saved_track")
            if os.path.isfile(os.path.join(tup[0], tup[1])):
                self.mpanel.doLoadFile(tup[0], tup[1])
                if tup[2]:
                    self.mpanel.media.player.time_pos = tup[2]

        if self.data.exists("audio_device"):
            item = self.audio_devices_menu.GetByName(self.mpanel.media.find_device(self.data.get("audio_device")))
            if item:
                item.Check(True)
                self.mpanel.media.player.audio_device = self.data.get("audio_device")

    def save(self):
        self.data.add("subtitle_delay", self.mpanel.subtitles.delay_by)
        self.data.add("volume", self.mpanel.media.player.volume)
        self.data.add("audio_device", self.mpanel.media.player.audio_device)
        if self.mpanel.subtitles.last_subtitle:
            self.data.add("last_subtitle", self.mpanel.subtitles.last_subtitle)
        if self.mpanel.media.last_audio_track:
            self.data.add("last_audio_track", self.mpanel.media.last_audio_track)
        if os.path.isfile(os.path.join(self.mpanel.media.dir, self.mpanel.media.file)):
            self.data.add(
                "saved_track",
                (
                    self.mpanel.media.dir,
                    self.mpanel.media.file,
                    self.mpanel.media.player.time_pos,
                ),
            )
        self.data.save()

    def onClose(self, event):
        self.save()
        speech_terminate()
        self.mpanel.subtitles.destroy()
        self.mpanel.media.onStop()
        self.mpanel.media.player.terminate()
        wx.CallAfter(self.Destroy)

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        if keycode == wx.WXK_PAGEUP:
            self.mpanel.media.previous_file()
        if keycode == wx.WXK_PAGEDOWN:
            self.mpanel.media.next_file()

        if keycode == ord("."):
            self.mpanel.media.next_chapter()
            self.mpanel.subtitles.reset()
        if keycode == ord(","):
            self.mpanel.media.previous_chapter()
            self.mpanel.subtitles.reset()

        if keycode == wx.WXK_DOWN and self.mpanel.media.player.volume > 0:
            vol = self.mpanel.media.player.volume
            self.mpanel.media.player.volume = vol - 5
            speak(f"{math.floor(vol - 5)}%")
        if keycode == wx.WXK_UP and self.mpanel.media.player.volume < 200:
            vol = self.mpanel.media.player.volume
            self.mpanel.media.player.volume = vol + 5
            speak(f"{math.floor(vol + 5)}%")

        if keycode == wx.WXK_RIGHT:
            val = 5
            if altDown:
                val = 60
            if controlDown:
                val = 30
            self.mpanel.media.player.command("seek", val)
            self.mpanel.subtitles.reset()

        if keycode == wx.WXK_LEFT:
            val = 5
            if altDown:
                val = 60
            if controlDown:
                val = 30
            self.mpanel.media.player.command("seek", -val)
            self.mpanel.subtitles.reset()
        if keycode == wx.WXK_HOME:
            self.mpanel.media.player.time_pos = 0.0
            self.mpanel.subtitles.reset()

        if keycode == ord("P"):
            time_pos = self.mpanel.media.player.time_pos if self.mpanel.media.player.time_pos else 0
            #length = self.mpanel.media.length if self.mpanel.media.length else 0
            length = self.mpanel.media.player.duration if self.mpanel.media.player.duration else 0
            speak(
                f"Current position, {str(timedelta(seconds = round(time_pos)))} elapsed of {str(timedelta(seconds = round(length)))}"
            )
        if keycode == wx.WXK_SPACE:
            if self.mpanel.media.state == utils.MediaState.paused:
                self.mpanel.media.onPlay()
            else:
                self.mpanel.media.onPause()
        else:
            event.Skip()

    def onLoadUrl(self, event):
        with wx.TextEntryDialog(self, "Enter URL") as dlg:
            r = dlg.ShowModal()
            if r != wx.ID_OK:
                return
            self.mpanel.media.load("", dlg.GetValue(), True)

    def onLoadFile(self, evt):
        dlg = wx.FileDialog(self, "Select a media file")
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetDirectory()
            file = dlg.GetFilename()
            self.mpanel.doLoadFile(dir, file)

    def onLoadSubtitle(self, evt):
        with wx.FileDialog(
            self,
            wildcard="Subtitle files (*.srt;*.ass;*.ssa)|*.srt;*.ass;*.ssa",
            message="Select a subtitle file",
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.mpanel.subtitles.doLoadSubtitle(dir, file)


class LogRedirector:
    def __init__(self, level):
        self.level = level

    def write(self, text):
        if text.strip():
            self.level(text)

    def flush(self):
        pass


def main():
    logging.basicConfig(
        filename="mediasplash.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(levelname)s: %(module)s: %(funcName)s: %(asctime)s.\n%(message)s",
    )

    def exchandler(type, exc, tb):
        logging.error("".join([str(i) for i in traceback.format_exception(type, exc, tb)]))

    sys.excepthook = exchandler
    sys.stderr = LogRedirector(logging.warning)
    sys.stdout = LogRedirector(logging.info)
    logging.info(f"running on {platform.platform()}")
    logging.info(f"python version: {sys.version}")
    logging.info(f"wx version: {wx.version()}")
    logging.info(f"machine name: {platform.machine()}")
    app = wx.App()
    frame = Main(app)
    frame.Show()
    app.MainLoop()
