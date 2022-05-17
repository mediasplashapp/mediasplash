from datetime import timedelta
from media_panel import MediaPanel
from data_manager import DataManager as dm
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
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.subtitleSelectMenu = self.fileMenu.Append(
            wx.ID_ANY, "Change subtitle.\tAlt+C"
        )
        self.subtitleOpen = self.fileMenu.Append(wx.ID_ANY, "Open subtitle...\tAlt+O")
        self.subDelay = self.fileMenu.Append(
            wx.ID_ANY, "Change subtitle delay...\tAlt+D"
        )
        self.exit_item = self.fileMenu.Append(wx.ID_EXIT, "Quit\tCtrl+Q")
        self.menubar.Append(self.fileMenu, "&file")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.Bind(wx.EVT_MENU, self.mpanel.subtitle_select, self.subtitleSelectMenu)
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, self.subtitleOpen)
        self.Bind(wx.EVT_MENU, lambda event: self.mpanel.delay_set(), self.subDelay)
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), self.exit_item)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.data = dm("config.json")
        self.load()

    def load(self):
        self.data.load()
        if self.data.exists("subtitle_delay"):
            self.mpanel.delay_by = int(self.data.get("subtitle_delay"))

    def save(self):
        self.data.add("subtitle_delay", self.mpanel.delay_by)
        self.data.save()

    def onClose(self, event):
        self.save()
        if self.mpanel.temp_dir:  # Make sure to clean up the directory before closing.
            self.mpanel.temp_dir.cleanup()
        self.mpanel.onStop(None)
        if self.mpanel.media:
            self.mpanel.media.release()
        self.mpanel.player.release()
        self.mpanel.instance.release()
        wx.CallAfter(self.Destroy)

    def onKeyHook(self, event):
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        if keycode == wx.WXK_DOWN and self.mpanel.player.audio_get_volume() > 0:
            self.mpanel.player.audio_set_volume(
                self.mpanel.player.audio_get_volume() - 5
            )
            speak(f"{self.mpanel.player.audio_get_volume()}%")
        if keycode == wx.WXK_UP and self.mpanel.player.audio_get_volume() < 200:
            self.mpanel.player.audio_set_volume(
                self.mpanel.player.audio_get_volume() + 5
            )
            speak(f"{self.mpanel.player.audio_get_volume()}%")

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
        if keycode == wx.WXK_SPACE:
            if self.mpanel.state == utils.MediaState.paused:
                self.mpanel.onPlay()
            else:
                self.mpanel.onPause()
        else:
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
    sys.stderr = LogRedirector(logging.warning)
    sys.stdout = LogRedirector(logging.info)
    logging.info(f"running on {platform.platform()}")
    logging.info(f"python version: {sys.version}")
    logging.info(f"wx version: {wx.version()}")
    logging.info(f"machine name: {platform.machine()}")

    compiled = getattr(locals(), "__compiled__", False)
    with tolk.tolk(not compiled):
        app = wx.App()
        frame = Main(app)
        frame.Show()
        app.MainLoop()
