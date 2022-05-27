import subtitles.handler
import logging
from misc import utils
from cytolk.tolk import speak
from . import dialogs
import pysubs2
import reader
import tempfile
import wx
import os
from media.handler import Media


class MediaPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetLabel("Media controls")
        self.SetBackgroundColour(wx.BLACK)
        self.frame = parent
        self.media = Media(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.queue_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onQueueTimer, self.queue_timer)
        self.subtitles = subtitles.handler.SubHandler(self)

    def onTimer(self, event):
        self.media.update()
        self.subtitles.update()

    def onQueueTimer(self, event):
        self.subtitles.on_queue()


    def audio_tracks_set(self):
        self.frame.audio_tracks_menu.Clear()
        audio_tracks = self.media.player.audio_get_track_description()
        for i in audio_tracks[1:]:
            self.frame.audio_tracks_menu.Append(
                wx.ID_ANY, i[1].decode("utf-8"), kind=wx.ITEM_RADIO
            )


    def doLoadFile(self, file, dir):
        self.media.onStop()
        self.timer.Stop()
        self.frame.audio_tracks_menu.Clear()
        self.subtitles.destroy()
        self.frame.SetTitle(f"{file} mediaslash")
        self.media.load(dir, file)
        self.subtitles.load(dir, file)
        self.audio_tracks_set()
        self.timer.Start(50)
        self.queue_timer.Start(50)

