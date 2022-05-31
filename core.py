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
from data_manager import DataManager as dm
from gui import dialogs, messageBox
from globals import info
from datetime import timedelta
import webbrowser
import logging
from misc import utils, update_check
from gui import custom_controls
import platform
import traceback
import wx
from cytolk import tolk
from cytolk.tolk import speak

try:
    from gui.media_panel import MediaPanel
except FileNotFoundError:
    import ctypes

    ctypes.windll.user32.MessageBoxW(
        None, "Vlc not found. Please install Vlc 64 bit 3.0 or later", "Error", 0x10
    )
    sys.exit()


class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title="mediasplash")
        self.mpanel = MediaPanel(self)
        self.app = app
        self.mpanel.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.Centre()
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.subtitleOpen = self.fileMenu.Append(wx.ID_ANY, "Open subtitle...\tAlt+O")
        self.exit_item = self.fileMenu.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self.menubar.Append(self.fileMenu, "&file")
        self.mediaMenu = wx.Menu()
        self.subtitleSelectMenu = self.mediaMenu.Append(
            wx.ID_ANY, "Change subtitle.\tAlt+C"
        )
        self.subDelay = self.mediaMenu.Append(
            wx.ID_ANY, "Change subtitle delay...\tAlt+D"
        )
        self.jumpItem = self.mediaMenu.Append(wx.ID_ANY, "Jump to...\tctrl+J")
        self.audio_tracks_menu = custom_controls.ClearableMenu()
        self.mediaMenu.AppendSubMenu(self.audio_tracks_menu, "Audio tracks")
        self.menubar.Append(self.mediaMenu, "&Media")
        self.helpMenu = wx.Menu()
        self.updateCheck = self.helpMenu.Append(wx.ID_ANY, "Check for updates...")
        self.fileAbout = self.helpMenu.Append(wx.ID_ABOUT)
        self.menubar.Append(self.helpMenu, "&Help")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.Bind(wx.EVT_MENU, self.about, self.fileAbout)
        self.Bind(wx.EVT_MENU, self.onUpdateCheck, self.updateCheck)

        self.Bind(
            wx.EVT_MENU, self.mpanel.subtitles.subtitle_select, self.subtitleSelectMenu
        )
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, self.subtitleOpen)
        self.Bind(
            wx.EVT_MENU, lambda event: self.mpanel.subtitles.delay_set(), self.subDelay
        )
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), self.exit_item)
        self.Bind(wx.EVT_MENU, self.on_jump, self.jumpItem)
        self.audio_tracks_menu.Bind(wx.EVT_MENU, self.audio_track_set)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.data = dm(os.path.join(info.data_path, "config.json"))
        self.load()

    def about(self, event):
        with dialogs.AboutDialog(self) as dlg:
            dlg.ShowModal()

    def onUpdateCheck(self, event):
        updateData = update_check.check()
        if updateData:
            if messageBox(self, f"A new update of {info.name} is available. New version: {'.'.join(updateData)}. Download the update now?", "Update available", wx.YES_NO | wx.YES_DEFAULT) == wx.ID_YES:
                webbrowser.open_new("https://github.com/mohamedSulaimanAlmarzooqi/mediasplash/releases/latest/download/mediasplash.zip")
            return
        messageBox(self, "No update found", "No updates", wx.ICON_WARNING)

    def on_jump(self, event):
        with wx.TextEntryDialog(
            self, "Type a position to quickly jump too, example, 5.30", "Go to"
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK and dlg.GetValue().strip():
                delta = None
                value = dlg.GetValue().split(".")
                value = [int(v) for v in value if v.isdigit()]
                if not value:
                    return
                if len(value) == 2:
                    delta = timedelta(minutes=value[0], seconds=value[1])
                elif len(value) == 1:
                    delta = timedelta(minutes = value[0])
                elif len(value) == 3:
                    delta = timedelta(hours = value[0], minutes = value[1], seconds = value[2])
                if not delta or delta.total_seconds() * 1000 > self.mpanel.media.length:
                    messageBox(self, "input is not valid", "Error", wx.ICON_ERROR)
                self.mpanel.media.player.set_position(
                    round(delta.total_seconds() * 1000) / self.mpanel.media.length
                )
                self.mpanel.subtitles.queue_reset()

    def audio_track_set(self, event):
        result = self.audio_tracks_menu.GetChecked().GetItemLabelText()
        tracks = self.mpanel.media.player.audio_get_track_description()
        for i in tracks[1:]:
            if i[1].decode("utf-8") == result:
                self.mpanel.media.player.audio_set_track(i[0])

    def load(self):
        self.data.load()
        if self.data.exists("subtitle_delay"):
            self.mpanel.subtitles.delay_by = int(self.data.get("subtitle_delay"))
            self.mpanel.media.player.video_set_spu_delay(
                int(self.data.get("subtitle_delay"))
            )

    def save(self):
        self.data.add("subtitle_delay", self.mpanel.subtitles.delay_by)
        self.data.save()

    def onClose(self, event):
        self.save()
        self.mpanel.subtitles.destroy()
        self.mpanel.media.onStop()
        if self.mpanel.media.media:
            self.mpanel.media.media.release()
        self.mpanel.media.player.release()
        self.mpanel.media.instance.release()
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
            self.mpanel.media.player.next_chapter()
            self.mpanel.subtitles.queue_reset()
        if keycode == ord(","):
            self.mpanel.media.player.previous_chapter()
            self.mpanel.subtitles.queue_reset()

        if keycode == wx.WXK_DOWN and self.mpanel.media.player.audio_get_volume() > 0:
            vol = self.mpanel.media.player.audio_get_volume()
            self.mpanel.media.player.audio_set_volume(vol - 5)
            speak(f"{vol - 5}%")
        if keycode == wx.WXK_UP and self.mpanel.media.player.audio_get_volume() < 200:
            vol = self.mpanel.media.player.audio_get_volume()
            self.mpanel.media.player.audio_set_volume(vol + 5)
            speak(f"{vol + 5}%")

        if keycode == wx.WXK_RIGHT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.mpanel.media.player.set_position(
                (self.mpanel.media.player.get_time() + val) / self.mpanel.media.length
            )
            self.mpanel.subtitles.queue_reset()

        if keycode == wx.WXK_LEFT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.mpanel.media.player.set_position(
                (self.mpanel.media.player.get_time() - val) / self.mpanel.media.length
            )
            self.mpanel.subtitles.queue_reset()
        if keycode == wx.WXK_HOME:
            self.mpanel.media.player.set_position(0)
            self.mpanel.subtitles.queue_reset()

        if keycode == ord("P"):
            speak(
                f"Current position, {str(timedelta(seconds = round((self.mpanel.media.player.get_time() / 1000))))} elapsed of {str(timedelta(seconds = round((self.mpanel.media.length / 1000))))}"
            )
        if keycode == wx.WXK_SPACE:
            if self.mpanel.media.state == utils.MediaState.paused:
                self.mpanel.media.onPlay()
            else:
                self.mpanel.media.onPause()
        else:
            event.Skip()

    def onLoadFile(self, evt):
        with wx.FileDialog(self, "Select a media file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.mpanel.doLoadFile(file, dir)

    def onLoadSubtitle(self, evt):
        with wx.FileDialog(
            self,
            wildcard="Subtitle files (*.srt;*.ass;*.ssa)|*.srt;*.ass;*.ssa",
            message="Select a subtitle file",
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.mpanel.subtitles.doLoadSubtitle(file, dir)


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
        logging.error(
            "".join([str(i) for i in traceback.format_exception(type, exc, tb)])
        )

    sys.excepthook = exchandler
    sys.stderr = LogRedirector(logging.warning)
    sys.stdout = LogRedirector(logging.info)
    logging.info(f"running on {platform.platform()}")
    logging.info(f"python version: {sys.version}")
    logging.info(f"wx version: {wx.version()}")
    logging.info(f"machine name: {platform.machine()}")

    with tolk.tolk():
        app = wx.App()
        frame = Main(app)
        frame.Show()
        app.MainLoop()
