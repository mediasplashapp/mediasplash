from datetime import datetime
from datetime import timedelta
from pysubparser import parser
import sys
sys.dont_write_byte_code = True
from pysubparser.cleaners import formatting
import reader
import pyperclip
import tempfile
import wx
import wx.media
from cytolk import tolk
from cytolk.tolk import speak
import os
from platform_utils.paths import module_path, is_frozen, embedded_data_path

os.add_dll_directory(os.path.join(embedded_data_path(),'libs'))
from enum import Enum
import vlc
class MediaState(Enum):
    neverPlayed = 0
    stopped = 1
    paused = 2
    playing = 3

class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title = "mediaslash")
        self.panel = wx.Panel(self)
        self.app = app
        self.state = MediaState.neverPlayed
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.queue_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onQueueTimer, self.queue_timer)
        # The delaying period for speaking subtitles(In milliseconds.)
        self.delay_by = 0
        self.index = 0
        self.queue = []
        self.queue_index = 0
        self.subtitle_handler = None
        # This exists so we can handle events, Not sure why if there's none it's just won't respond to any.
        self.mc = wx.media.MediaCtrl(self.panel, style=wx.SIMPLE_BORDER)
        self.mc.Bind(wx.EVT_CHAR, self.onKeyPress)
        self.mc.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.panel.GetHandle())
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN, "&Open")
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
        if sum(1 for _ in self.subtitle_handler) == 0:
            return
        start = self.subtitle_handler[self.index].start
        end = self.subtitle_handler[self.index].end
        current = datetime.fromtimestamp(self.player.get_time() / 1000.0).time()
        if current >= start and current <= end:
            self.queue.append(self.subtitle_handler[self.index].text)
            if self.index < sum(1 for _ in self.subtitle_handler):
                self.index += 1

    def onQueueTimer(self, event):
        if len(self.queue) == 0 or self.index > len(self.queue):
            return
        speak(self.queue[self.queue_index])
        self.queue_index += 1
    def onClose(self, event):
        if self.temp_dir: # Make sure to clean up the directory before closing.
            self.temp_dir.cleanup()
        sys.exit()
    def onKeyHook(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RIGHT:
            self.player.set_position((self.player.get_time() + 5000) / self.player.get_length())
        if keycode == wx.WXK_LEFT:
            self.player.set_position((self.player.get_time() - 5000) / self.player.get_length())
        event.Skip()

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == ord("p"):
            speak(f"Current position, {str(timedelta(seconds = round((self.player.get_time() / 1000))))} elapsed of {str(timedelta(seconds = round((self.player.get_length() / 1000))))}")

        if keycode == wx.WXK_SPACE:
            if self.state == MediaState.paused:
                self.player.play()
            else:
                self.player.pause()
        if keycode == wx.WXK_CONTROL_O:
            self.onLoadFile()
        event.Skip()
    def onLoadFile(self, evt = None):
        dlg = wx.FileDialog(self, "Open", "", "",
            "All files (*.*)|*.*", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            dir  = dlg.GetDirectory()
            file = dlg.GetFilename()
            self.doLoadFile(file, dir)
        dlg.Destroy()
        
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
        self.subtitles = reader.generate_subtitles(os.path.join(dir, file), self.temp_dir)
        for (i, j) in self.subtitles.values():
            if i == 1:
                self.subtitle = j
        if self.subtitle == "":
            self.subtitle = list(self.subtitles)[0][1]
        self.subtitle_handler = parser.parse(self.subtitle)
        self.timer.Start()
        pyperclip.copy(str(self.player.video_get_spu_description()))
        
    def onPlay(self, evt):
        if self.player.get_media():
            self.player.play()
            self.queue_timer.Start(self.delay_by)
        if self.state != MediaState.playing: self.state = MediaState.playing
    
    def onPause(self, evt):
        if self.player.get_media():
            self.player.pause()
            self.queue_timer.Stop()
        if self.state != MediaState.paused: self.state = MediaState.paused

    
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