"""
    Mediaslash, A simple media player with screen reader subtitle support.
    Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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

class AboutDialog(wx.Dialog):
    def __init__(self, frame):
        super().__init__(frame, title = "About mediaslash")
        box = wx.BoxSizer()
        self.ctrl = wx.TextCtrl(self, value = """
    Mediaslash, A simple media player with screen reader subtitle support.
    Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.TE_RICH2)
        box.Add(self.ctrl)
        box.Add(self.CreateButtonSizer(wx.CLOSE))
        self.SetSizer(box)
        self.ctrl.SetFocus()
