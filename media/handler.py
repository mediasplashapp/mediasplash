import vlc
import os
import wx
from misc import utils

class Media:
    def __init__(self, parent):
        self.panel = parent
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
        self.media = self.instance.media_new(os.path.join(dir, file))
        self.player.set_media(self.media)
        self.onPlay()

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

