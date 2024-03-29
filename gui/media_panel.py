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

import subtitles.handler
import wx
import global_vars
from media.handler import Media
from misc import utils


class MediaPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, style=wx.WANTS_CHARS)
        self.SetLabel("Media controls")
        self.SetBackgroundColour(wx.BLACK)
        self.frame = parent
        self.media = Media(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.subtitles = subtitles.handler.SubHandler(self)

    def onTimer(self, event):
        self.subtitles.update()

    def audio_devices_set(self):
        devices = self.media.player.audio_device_list
        for i in devices:
            self.frame.audio_devices_menu.Append(wx.ID_ANY, i["description"], kind=wx.ITEM_RADIO)

    def audio_tracks_set(self):
        self.frame.audio_tracks_menu.Clear()
        audio_tracks = utils.generate_track_info(self.media.player.track_list, "audio")
        for i in audio_tracks:
            self.frame.audio_tracks_menu.Append(wx.ID_ANY, i, kind=wx.ITEM_RADIO)

    def doLoadFile(self, dir, file):
        self.media.onStop()
        self.timer.Stop()
        self.frame.audio_tracks_menu.Clear()
        self.subtitles.destroy()
        self.media.load(dir, file)
        self.subtitles.load(dir, file)
        self.audio_tracks_set()
        self.timer.Start(10)
        self.frame.set_audio_track(self.media.last_audio_track)
        self.subtitles.set_subtitle(self.subtitles.last_subtitle)
        self.frame.SetTitle(f"{self.media.title} - {global_vars.info.name}")
