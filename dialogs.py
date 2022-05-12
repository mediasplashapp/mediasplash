import wx


class SubtitleSelect(wx.Dialog):
    def __init__(self, frame):
        super().__init__(frame, title = "Select a subtitle")
        self.pnl = wx.Panel(self)
        box = wx.BoxSizer()
        gbox_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.pnl, "Subtitles")
        gbox = gbox_sizer.GetStaticBox()
        gbox_sizer.Add(wx.StaticText(gbox, label = "Subtitles:"))
        subtitles = frame.stringify_subtitles()
        self.subtitle_select = wx.Choice(gbox, choices = subtitles)
        gbox_sizer.Add(self.subtitle_select)
        box.Add(gbox_sizer)
        box.Add(wx.Button(self.pnl, wx.ID_OK))
        box.Add(wx.Button(self.pnl, wx.ID_CANCEL))
        self.pnl.SetSizer(box)
