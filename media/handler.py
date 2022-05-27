import vlc
import os
import wx
from misc import utils

supported_media = (".mp3", ".mp4", ".mkv", ".ogg", ".opus", ".wav", ".aac", ".m4a", ".flac")

class Media:
    def __init__(self, parent):
        self.panel = parent
        self.dir = ""
        self.file = ""
        self.state = utils.MediaState.neverPlayed
        self.instance = vlc.Instance("--no-video")
        self.player: vlc.MediaPlayer = self.instance.media_player_new()
        self.media = None
        self.player.set_hwnd(self.panel.GetHandle())
        self.manager: vlc.EventManager = self.player.event_manager()

    def update(self):
        if self.player.get_state() == vlc.State.Ended:
            self.onStop()


    def load(self, dir, file):
        self.dir = dir
        self.file = file
        self.media = self.instance.media_new(os.path.join(dir, file))
        self.player.set_media(self.media)
        self.onPlay()

    def next_file(self):
        if not self.dir or not self.file:
            return
        files = os.listdir(self.dir)
        if not self.file in files:
            return
        file_index = files.index(self.file)
        for i in files[file_index:]:
            if not i == self.file and os.path.splitext(i)[1] in supported_media:
                self.panel.doLoadFile(i, self.dir)
                break

    def previous_file(self):
        if not self.dir or not self.file:
            return
        files = os.listdir(self.dir)
        if not self.file in files:
            return
        file_index = files.index(self.file)
        for i in reversed(files[:file_index]):
            if not i == self.file and os.path.splitext(i)[1] in supported_media:
                self.panel.doLoadFile(i, self.dir)
                break

    def onPlay(self):
        if self.player.get_media():
            self.player.play()
        if self.state != utils.MediaState.playing:
            self.state = utils.MediaState.playing

    def onPause(self):
        if self.player.get_media():
            self.player.pause()
        if self.state != utils.MediaState.paused:
            self.state = utils.MediaState.paused

    def onStop(self):
        self.panel.subtitles.queue_reset()
        self.player.stop()

