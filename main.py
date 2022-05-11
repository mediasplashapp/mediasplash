from datetime import datetime
from datetime import timedelta
from pysubparser import parser
import ass
import sys
import reader
import pyperclip
import tempfile
import wx
from cytolk import tolk
from cytolk.tolk import speak
import os
from enum import Enum
import vlc

os.add_dll_directory(os.path.join(os.getcwd(), "lib"))


class MediaState(Enum):
    neverPlayed = 0
    stopped = 1
    paused = 2
    playing = 3


class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title="mediaslash")
        self.panel = wx.Panel(self)
        self.app = app
        self.state = MediaState.neverPlayed
        self.timer = wx.Timer(self)
        self.timer.Bind(wx.EVT_TIMER, self.onTimer)
        self.queue_timer = wx.Timer(self)
        self.queue_timer.Bind(wx.EVT_TIMER, self.onQueueTimer)
        # The delaying period for speaking subtitles(In milliseconds.)
        self.delay_by = 0
        self.index = 0
        self.queue = []
        self.queue_index = 0
        self.subtitle_handler = None
        # This exists so we can handle events, Not sure why if there's none it's just won't respond to any.
        self.panel.Bind(wx.EVT_KEY_UP, self.onKeyPress)
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.panel.GetHandle())
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.menubar.Append(self.fileMenu, "&file")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        # Temporary directory, For storing extracted subtitles from media, If any.
        self.temp_dir = None
        # The list of subtitles, A dictionary with keys of value string, For the name, And values for the value tuple (Default, subtitle_path)
        self.subtitles = {}
        # The current subtitle file selected.
        self.subtitle = ""

    def onTimer(self, event):
        for i in self.subtitle_handler.events:
            start = i.start
            end = i.end
            current = timedelta(milliseconds = self.player.get_time())
            if current >= start and current <= end:
                self.queue.append(i.text)

    def onQueueTimer(self, event):
        if len(self.queue) == 0 or self.queue_index > len(self.queue) -1:
            return
        speak(self.queue[self.queue_index])
        self.queue_index += 1

    def onClose(self, event):
        if self.temp_dir:  # Make sure to clean up the directory before closing.
            self.temp_dir.cleanup()
        sys.exit()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RIGHT:
            self.player.set_position(
                (self.player.get_time() + 5000) / self.player.get_length()
            )
        if keycode == wx.WXK_LEFT:
            self.player.set_position(
                (self.player.get_time() - 5000) / self.player.get_length()
            )

        if keycode == ord("p"):
            speak(
                f"Current position, {str(timedelta(seconds = round((self.player.get_time() / 1000))))} elapsed of {str(timedelta(seconds = round((self.player.get_length() / 1000))))}"
            )

        if keycode == wx.WXK_SPACE:
            if self.state == MediaState.paused:
                self.player.play()
            else:
                self.player.pause()
        if keycode == wx.WXK_CONTROL_O:
            self.onLoadFile()
        event.Skip()

    def onLoadFile(self, evt):
        with wx.FileDialog(self, "Select a media file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
            self.doLoadFile(file, dir)

    def doLoadFile(self, file, dir):
        self.onStop(None)
        self.timer.Stop()
        self.media = self.instance.media_new(os.path.join(dir, file))
        self.player.set_media(self.media)
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None
        if (title := self.player.get_title()) == -1:
            title = file
        self.SetTitle(title)
        self.onPlay(None)
        self.state = MediaState.playing
        self.player.audio_set_volume(70)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.subtitles = reader.generate_subtitles(
            os.path.join(dir, file), self.temp_dir
        )
        for (i, j) in self.subtitles.values():
            if i == 1:
                self.subtitle = j
                break
        if self.subtitle == "":
            self.subtitle = list(self.subtitles)[0][1]
        #self.subtitle_handler = parser.parse(self.subtitle)
        with open(self.subtitle, "r", encoding='utf_8_sig') as f:
            self.subtitle_handler = ass.parse(f)
        self.timer.Start()

    def onPlay(self, evt):
        if self.player.get_media():
            self.player.play()
            self.queue_timer.Start(self.delay_by)
        if self.state != MediaState.playing:
            self.state = MediaState.playing

    def onPause(self, evt):
        if self.player.get_media():
            self.player.pause()
            self.queue_timer.Stop()
        if self.state != MediaState.paused:
            self.state = MediaState.paused

    def onStop(self, evt):
        if self.player.get_media():
            self.player.stop()

    def seek(self, offset):
        self.player.Seek(offset)


with tolk.tolk():
    app = wx.App()
    frame = Main(app)
    frame.Show(1)
    app.MainLoop()
