from datetime import timedelta
import time
import logging
from pathlib import Path
from cleaner import clean
from data_manager import DataManager as dm
import dialogs
import platform
import pyperclip
import traceback
import pysubs2
import sys
import reader
import tempfile
import wx
from cytolk import tolk
from cytolk.tolk import speak
import os
from enum import Enum
import vlc

os.add_dll_directory(os.path.join(os.getcwd(), "lib"))

supported_subtitles = (".ass", ".ssa", ".srt")

def check_for_similar_subtitles(dir, file):
    p = Path(os.path.join(dir, file))
    final = {}
    filename = p.stem
    for i in supported_subtitles:
        if p.with_suffix(i).exists():
            final[filename] = (0, f"{os.path.join(dir, filename)}{i}")
            clean(f"{os.path.join(dir, filename)}{i}")
    return final

def get_subtitle_tuple(sub):
    return (sub.start, sub.end, sub.text)

class MediaState(Enum):
    neverPlayed = 0
    stopped = 1
    paused = 2
    playing = 3

class MediaPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.state = MediaState.neverPlayed
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.GetHandle())
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
        # The list of subtitles, A dictionary with keys of value string, For the name, And values for the value tuple (Default, subtitle_path)
        self.subtitles = {}
        self.subtitle_text = ""
        # The current subtitle file selected.
        self.subtitle = ""
        self.processed_events = []
        # Temporary directory, For storing extracted subtitles from media, If any.
        self.temp_dir = None
        self.data = dm("config.json")
        self.load()

    def load(self):
        self.data.load()
        if self.data.exists("subtitle_delay"):
            self.delay_by = int(self.data.get("subtitle_delay"))
    def save(self):
        self.data.add("subtitle_delay", self.delay_by)
        self.data.save()
    def onTimer(self, event):
        if self.player.get_state() == vlc.State.Ended:
            self.onStop(None)
            return
        if get_subtitle_tuple(self.subtitle_handler[self.index]) in self.processed_events:
            self.check_for_subtitle()
            return
        start = timedelta(milliseconds = self.subtitle_handler.events[self.index].start + self.delay_by)
        end = timedelta(milliseconds = self.subtitle_handler[self.index].end + self.delay_by)
        current = timedelta(milliseconds=self.player.get_time())
        if current >= start and current <= end:
            self.queue.append(self.subtitle_handler[self.index].text)
            self.processed_events.append(get_subtitle_tuple(self.subtitle_handler[self.index]))
            self.index += 1
            return
        self.check_for_subtitle()
    def check_for_subtitle(self):
        for (val, i) in enumerate(self.subtitle_handler):
            if get_subtitle_tuple(i) in self.processed_events:
                continue
            start = timedelta(milliseconds = i.start + self.delay_by)
            end = timedelta(milliseconds = i.end + self.delay_by)
            current = timedelta(milliseconds=self.player.get_time())
            if current >= start and current <= end:
                self.queue.append(i.text)
                self.processed_events.append(get_subtitle_tuple(i))
                self.index = val
                break

    def onQueueTimer(self, event):
        if len(self.queue) == 0 or self.queue_index > len(self.queue) - 1:
            return
        speak(self.queue[self.queue_index].replace(r"\N", "\n"))
        self.queue.remove(self.queue[self.queue_index])

    def stringify_subtitles(self):
        final_list = []
        for i in self.subtitles:
            final_list.append(i)
        return final_list

    def delay_set(self):
        with dialogs.TextField(self, "Define subtitle delay(In milliseconds)", value = str(self.delay_by)) as dlg:
            r = dlg.ShowModal()
            if r != wx.ID_OK:
                return
            val = dlg.text.GetValue()
            if not val:
                return
            try:
                self.delay_by = int(val)
            except ValueError:
                r = wx.MessageBox(
                    "Invalid value, Must be an integer",
                    "Error",
                    wx.ICON_ERROR,
                )
                return
            speak(f"Subtitle delay set to {self.delay_by}", True)

    def subtitle_select(self, event = None):
        if len(self.subtitles) == 0 or not self.subtitle_handler:
            return
        with dialogs.SubtitleSelect(self) as dlg:
            r = dlg.ShowModal()
            if r != wx.ID_OK:
                return
            sub = dlg.subtitle_select.GetString(dlg.subtitle_select.Selection)
            if not sub:
                wx.MessageBox(
                    "Aborting...",
                    "No subtitle selected",
                    wx.ICON_ERROR,
                )
                return
            if sub not in self.subtitles:
                wx.MessageBox(
                    "There was an error while trying to parse the selected subtitle... Please try again later.",
                    "Fatal error",
                    wx.ICON_ERROR,
                )
                return
            self.subtitle = self.subtitles[sub][1]
            self.subtitle_handler = pysubs2.load(self.subtitle, encoding = "utf-8")

    def queue_reset(self):
        if len(self.subtitles) == 0 or not self.subtitle_handler or len(self.subtitle_handler) == 0:
            return
        self.queue.clear()
        self.queue_index = 0
        self.index = 0
        self.processed_events.clear()
        for (val, i) in enumerate(self.subtitle_handler):
            start = timedelta(milliseconds = i.start + self.delay_by)
            end = timedelta(milliseconds = i.end + self.delay_by)
            current = timedelta(milliseconds=self.player.get_time())
            if current >= start and current <= end:
                self.queue.append(i.text)
                self.processed_events.append(get_subtitle_tuple(i))
                self.index = val

    def doLoadSubtitle(self, file, dir):
        clean(os.path.join(dir, file))
        try:
            self.subtitle_handler = pysubs2.load(os.path.join(dir, file), encoding = "utf-8")
        except:
            r = wx.MessageBox(
                "That file couldn't be loaded. Make sure it's a supported format and try again.",
                "File couldn't be loaded",
                wx.ICON_ERROR,
            )
            return
        self.subtitles[file] = (0, os.path.join(dir, file))

    def doLoadFile(self, file, dir):
        self.onStop(None)
        self.timer.Stop()
        self.media = self.instance.media_new(os.path.join(dir, file))
        self.player.set_media(self.media)
        if self.temp_dir:
            self.temp_dir.cleanup()
            self.temp_dir = None
        title = self.player.get_title()
        if title == -1:
            title = file
        self.frame.SetTitle(f"{title} mediaslash")
        self.onPlay(None)
        self.state = MediaState.playing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.subtitles = reader.generate_subtitles(
            os.path.join(dir, file), self.temp_dir
        )
        for (i, j) in self.subtitles.values():
            if i == 1:
                self.subtitle = j
                break
        if len(self.subtitles) > 0 and self.subtitle == "":
            self.subtitle = list(self.subtitles)[0][1]
        external_subs = check_for_similar_subtitles(dir, file)
        if len(external_subs) > 0:
            self.subtitles.update(external_subs)
            self.subtitle = next(iter(external_subs.items()))[1][1]
        #with open(self.subtitle, "r", encoding="utf-8") as f:
        #    self.subtitle_handler = ass.parse(f)
        self.subtitle_handler = pysubs2.load(self.subtitle, encoding = "utf-8")
        self.timer.Start()
        self.queue_timer.Start()

    def onPlay(self, evt = None):
        if self.player.get_media():
            self.player.play()
        if self.state != MediaState.playing:
            self.state = MediaState.playing

    def onPause(self, evt = None):
        if self.player.get_media():
            self.player.pause()
        if self.state != MediaState.paused:
            self.state = MediaState.paused

    def onStop(self, evt):
        self.queue_reset()
        if self.player.get_media():
            self.player.stop()

    def seek(self, offset):
        self.player.Seek(offset)


class Main(wx.Frame):
    def __init__(self, app):
        super().__init__(None, title="mediaslash")
        self.panel = MediaPanel(self)
        self.app = app
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.panel.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.Centre()
        self.Maximize(True)
        self.SetBackgroundColour(wx.BLACK)
        self.fileOpen = self.fileMenu.Append(wx.ID_OPEN)
        self.subtitleSelectMenu = self.fileMenu.Append(wx.ID_ANY, "Change subtitle.")
        self.subtitleOpen = self.fileMenu.Append(wx.ID_ANY, "Open subtitle")
        self.menubar.Append(self.fileMenu, "&file")
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU, self.onLoadFile, self.fileOpen)
        self.Bind(wx.EVT_MENU, self.panel.subtitle_select, self.subtitleSelectMenu)
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, self.subtitleOpen)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.table = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onLoadSubtitle, id = self.table)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord('O'), self.table)])
        self.SetAcceleratorTable(accel_tbl)

    def onClose(self, event):
        self.panel.save()
        if self.panel.temp_dir:  # Make sure to clean up the directory before closing.
            self.panel.temp_dir.cleanup()
        wx.CallAfter(self.Destroy)

    def onKeyHook(self, event):
        keycode = event.GetKeyCode()
        controlDown = event.CmdDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        if keycode == wx.WXK_DOWN and self.panel.player.audio_get_volume() > 5:
            self.panel.player.audio_set_volume(self.panel.player.audio_get_volume() -5)
        if keycode == wx.WXK_UP and self.panel.player.audio_get_volume() < 100:
            self.panel.player.audio_set_volume(self.panel.player.audio_get_volume() +5)

        if keycode == wx.WXK_RIGHT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.panel.player.set_position(
                (self.panel.player.get_time() + val) / self.panel.player.get_length()
            )
            self.panel.queue_reset()

        if keycode == wx.WXK_LEFT:
            val = 5000
            if altDown:
                val = 60000
            if controlDown:
                val = 30000
            self.panel.player.set_position(
                (self.panel.player.get_time() - val) / self.panel.player.get_length()
            )
            self.panel.queue_reset()
        if keycode == wx.WXK_HOME:
            self.panel.player.set_position(0)
            self.panel.queue_reset()

        if keycode == ord("P"):
            speak(
                f"Current position, {str(timedelta(seconds = round((self.panel.player.get_time() / 1000))))} elapsed of {str(timedelta(seconds = round((self.panel.player.get_length() / 1000))))}"
            )
        if controlDown and keycode == ord("D"):
            self.panel.delay_set()
        if controlDown and keycode == ord("S"):
            self.panel.subtitle_select()
        if keycode == wx.WXK_SPACE:
            if self.panel.state == MediaState.paused:
                self.panel.onPlay()
            else:
                self.panel.onPause()
        event.Skip()



    def onLoadFile(self, evt):
        with wx.FileDialog(self, "Select a media file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.panel.doLoadFile(file, dir)

    def onLoadSubtitle(self, evt):
        with wx.FileDialog(self, "Select a subtitle file") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                dir = dlg.GetDirectory()
                file = dlg.GetFilename()
                self.panel.doLoadSubtitle(file, dir)


if __name__ == "__main__":
    main()
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
