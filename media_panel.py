from datetime import timedelta
import logging
from cleaner import clean
import utils
from cytolk.tolk import speak
from data_manager import DataManager as dm
import dialogs
import pysubs2
import reader
import tempfile
import wx
import os
import vlc


class MediaPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.state = utils.MediaState.neverPlayed
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
        if (
            utils.get_subtitle_tuple(self.subtitle_handler[self.index])
            in self.processed_events
        ):
            self.check_for_subtitle()
            return
        start = timedelta(
            milliseconds=self.subtitle_handler.events[self.index].start + self.delay_by
        )
        end = timedelta(
            milliseconds=self.subtitle_handler[self.index].end + self.delay_by
        )
        current = timedelta(milliseconds=self.player.get_time())
        if current >= start and current <= end:
            self.queue.append(self.subtitle_handler[self.index].text)
            self.processed_events.append(
                utils.get_subtitle_tuple(self.subtitle_handler[self.index])
            )
            self.index += 1
            return
        self.check_for_subtitle()

    def check_for_subtitle(self):
        for (val, i) in enumerate(self.subtitle_handler):
            if utils.get_subtitle_tuple(i) in self.processed_events:
                continue
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(milliseconds=self.player.get_time())
            if current >= start and current <= end:
                self.queue.append(i.text)
                self.processed_events.append(utils.get_subtitle_tuple(i))
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
        with dialogs.SubDelay(
            self, "Define subtitle delay(In milliseconds)", value=str(self.delay_by)
        ) as dlg:
            r = dlg.ShowModal()
            if r == wx.ID_OK:
                val = dlg.spin.GetValue()
                self.delay_by = int(val)
                speak(f"Subtitle delay set to {self.delay_by}", True)

    def subtitle_select(self, event=None):
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
            self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")

    def queue_reset(self):
        if (
            len(self.subtitles) == 0
            or not self.subtitle_handler
            or len(self.subtitle_handler) == 0
        ):
            return
        self.queue.clear()
        self.queue_index = 0
        self.index = 0
        self.processed_events.clear()
        for (val, i) in enumerate(self.subtitle_handler):
            start = timedelta(milliseconds=i.start + self.delay_by)
            end = timedelta(milliseconds=i.end + self.delay_by)
            current = timedelta(milliseconds=self.player.get_time())
            if current >= start and current <= end:
                self.queue.append(i.text)
                self.processed_events.append(utils.get_subtitle_tuple(i))
                self.index = val

    def doLoadSubtitle(self, file, dir):
        clean(os.path.join(dir, file))
        try:
            self.subtitle_handler = pysubs2.load(
                os.path.join(dir, file), encoding="utf-8"
            )
        except Exception as e:
            logging.error("Could not load subtitles", exc_info=True)
            wx.MessageBox(
                "That file couldn't be loaded. Make sure it's a supported format and try again.",
                "File couldn't be loaded",
                wx.ICON_ERROR,
            )
            return
        self.subtitles[file] = (0, os.path.join(dir, file))
        self.timer.start()
        self.queue_timer.Start()

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
        self.state = utils.MediaState.playing
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
        external_subs = utils.check_for_similar_subtitles(dir, file)
        if len(external_subs) > 0:
            self.subtitles.update(external_subs)
            self.subtitle = next(iter(external_subs.items()))[1][1]
        # if os.path.isfile(self.subtitle):
        self.subtitle_handler = pysubs2.load(self.subtitle, encoding="utf-8")
        self.timer.Start()
        self.queue_timer.Start()

    def onPlay(self, evt=None):
        if self.player.get_media():
            self.player.play()
        if self.state != utils.MediaState.playing:
            self.state = utils.MediaState.playing

    def onPause(self, evt=None):
        if self.player.get_media():
            self.player.pause()
        if self.state != utils.MediaState.paused:
            self.state = utils.MediaState.paused

    def onStop(self, evt):
        self.queue_reset()
        if self.player.get_media():
            self.player.stop()

    def seek(self, offset):
        self.player.Seek(offset)
