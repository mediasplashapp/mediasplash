import wx
import wx.media
import os
from enum import Enum

class MediaState(Enum):
    neverPlayed = 0
    Stopped = 1
    Paused = 2
    Playing = 3

class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title = "media player")
        self.panel = wx.Panel(self)
        self.app = app
        self.state = MediaState.neverPlayed
        self.mc = wx.media.MediaCtrl(self.panel, style=wx.SIMPLE_BORDER)
        self.mc.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Bind(wx.media.EVT_MEDIA_LOADED, self.onPlay, self.mc)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN, "&Open")
        self.menubar.Append(self.fileMenu, "&file")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            if self.state == MediaState.Paused or self.state == MediaState.neverPlayed:
                self.mc.Play()
                self.state = MediaState.Playing
            else:
                self.mc.Pause()
                self.state = MediaState.Paused
        if keycode == wx.WXK_CONTROL_O:
            self.onLoadFile()
        event.Skip()
    def onLoadFile(self, evt = None):
        dlg = wx.FileDialog(self, "Open", "", "",
            "All files (*.*)|*.*", 
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.doLoadFile(path)
        dlg.Destroy()
        
    def doLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
        self.state = MediaState.neverPlayed
        
    def onPlay(self, evt):
        self.mc.Play()
        if self.state != MediaState.Playing: self.state = MediaState.Playing
    
    def onPause(self, evt):
        self.mc.Pause()
        if self.state != MediaState.Paused: self.state = MediaState.Paused

    
    def onStop(self, evt):
        self.mc.Stop()
    
    def onSeek(self, evt):
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    def onTimer(self, evt):
        offset = self.mc.Tell()
        self.slider.SetValue(offset)
        self.st_size.SetLabel('size: %s ms' % self.mc.Length())
        self.st_len.SetLabel('( %d seconds )' % (self.mc.Length()/1000))
        self.st_pos.SetLabel('position: %d ms' % offset)


app = wx.App()
frame = Main(app)
frame.Show(1)
app.MainLoop()