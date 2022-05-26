import wx
from wx.lib.intctrl import IntCtrl


class SubtitleSelect(wx.Dialog):
    def __init__(self, handle):
        super().__init__(handle.panel.frame, title="Select a subtitle")
        box = wx.BoxSizer()
        gbox_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Subtitles")
        gbox = gbox_sizer.GetStaticBox()
        gbox_sizer.Add(wx.StaticText(gbox, label="Subtitles:"))
        subtitles = handle.stringify_subtitles()
        self.subtitle_select = wx.Choice(gbox, choices=subtitles)
        gbox_sizer.Add(self.subtitle_select)
        box.Add(gbox_sizer)
        box.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizer(box)
        self.subtitle_select.SetFocus()


class SubDelay(wx.Dialog):
    def __init__(self, handle, title, value):
        super().__init__(handle.panel.frame, title=title)
        box = wx.BoxSizer()
        self.intctrl = IntCtrl(self, value = int(value), allow_none = False)
        box.Add(self.intctrl)
        box.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizer(box)
        self.intctrl.SetFocus()
