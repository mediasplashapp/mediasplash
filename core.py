from datetime import timedelta
from media_panel import MediaPanel
import logging
import utils
import platform
import traceback
import sys
import wx
from cytolk import tolk
from cytolk.tolk import speak
import os

os.add_dll_directory(os.path.join(os.getenv("programfiles"), r"videolan\vlc"))


class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title="mediaslash")
        self.mpanel = MediaPanel(self)
        self.app = app
        self.mpanel.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.Centre()
        self.Maximize(True)
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.subtitleSelectMenu = self.fileMenu.Append(wx.ID_ANY, "Change subtitle.")
        self.subtitleOpen = self.fileMenu.Append(wx.ID_ANY, "Open subtitle")
        self.menubar.Append(self.fileMenu, "&file")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.Bind(wx.EVT_MENU, self.mpanel.subtitle_select, self.subtitleSelectMenu)
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, self.subtitleOpen)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.table = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, id=self.table)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord("O"), self.table)])
        self.SetAcceleratorTable(accel_tbl)

    def onClose(self, event):
        self.mpanel.save()
        if self.mpanel.temp_dir:  # Make sure to clean up the directory before closing.
            self.mpanel.temp_dir.cleanup()
        wx.CallAfter(self.Destroy)

    def onKeyHook(self, event):
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        if keycode == wx.WXK_DOWN and self.mpanel.player.audio_get_volume() > 5:
            self.mpanel.player.audio_set_volume(
                self.mpanel.player.audio_get_volume() - 5
            )
        if keycode == wx.WXK_UP and self.mpanel.player.audio_get_volume() < 200:
            self.mpanel.player.audio_set_volume(
                self.mpanel.player.audio_get_volume() + 5
            )

        if keycode == wx.WXK_RIGHT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.mpanel.player.set_position(
                (self.mpanel.player.get_time() + val) / self.mpanel.player.get_length()
            )
            self.mpanel.queue_reset()

        if keycode == wx.WXK_LEFT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.mpanel.player.set_position(
                (self.mpanel.player.get_time() - val) / self.mpanel.player.get_length()
            )
            self.mpanel.queue_reset()
        if keycode == wx.WXK_HOME:
            self.mpanel.player.set_position(0)
            self.mpanel.queue_reset()

        if keycode == ord("P"):
            speak(
                f"Current position, {str(timedelta(seconds = round((self.mpanel.player.get_time() / 1000))))} elapsed of {str(timedelta(seconds = round((self.mpanel.player.get_length() / 1000))))}"
            )
        if controlDown and keycode == ord("D"):
            self.mpanel.delay_set()
        if controlDown and keycode == ord("S"):
            self.mpanel.subtitle_select()
        if keycode == wx.WXK_SPACE:
            if self.mpanel.state == utils.MediaState.paused:
                self.mpanel.onPlay()
            else:
                self.mpanel.onPause()
        event.Skip()

    def onLoadFile(self, evt):
        with wx.FileDialog(self, "Select a media file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.mpanel.doLoadFile(file, dir)

    def onLoadSubtitle(self, evt):
        with wx.FileDialog(self, "Select a subtitle file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.mpanel.doLoadSubtitle(file, dir)


def main():
    logging.basicConfig(
        filename="mediaslash.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(levelname)s: %(module)s: %(message)s: %(asctime)s",
    )

    def exchandler(type, exc, tb):
        logging.exception(
            "".join([str(i) for i in traceback.format_exception(type, exc, tb)])
        )

    sys.excepthook = exchandler
    logging.info(f"running on {platform.platform()}")
    logging.info(f"python version: {sys.version}")
    logging.info(f"wx version: {wx.version()}")
    logging.info(f"machine name: {platform.machine()}")

    with tolk.tolk(False):
        app = wx.App()
        frame = Main(app)
        frame.Show()
        app.MainLoop()
