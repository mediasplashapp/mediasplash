"""
    mediasplash, A simple media player with screen reader subtitle support.
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
import wx.adv
from wx.lib.intctrl import IntCtrl
from global_vars import info


class SubtitleSelect(wx.Dialog):
    def __init__(self, handle):
        super().__init__(handle.panel.frame, title="Select a subtitle")
        self.handle = handle
        box = wx.BoxSizer()
        gbox_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Subtitles")
        gbox = gbox_sizer.GetStaticBox()
        gbox_sizer.Add(wx.StaticText(gbox, label="Subtitles:"))
        subtitles = handle.stringify_subtitles()
        self.subtitle_select = wx.Choice(gbox, choices=subtitles)
        self.listbox = wx.ListBox(self, name="Subtitle info")
        gbox_sizer.Add(self.subtitle_select)
        gbox_sizer.Add(self.listbox)
        box.Add(gbox_sizer)
        box.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizer(box)
        self.Bind(wx.EVT_CHOICE, self.process_sub_selection)
        self.subtitle_select.SetFocus()

    def process_sub_selection(self, event):
        self.listbox.Clear()
        sel = self.subtitle_select.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        self.listbox.InsertItems(self.handle.subtitles[sel].stringify(), 0)


class SubDelay(wx.Dialog):
    def __init__(self, handle, title, value):
        super().__init__(handle.panel.frame, title=title)
        box = wx.BoxSizer()
        self.intctrl = IntCtrl(self, value=int(value), allow_none=False)
        box.Add(self.intctrl)
        box.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL))
        self.SetSizer(box)
        self.intctrl.SetFocus()


about_text = f"""{info.name}, A simple media player with screen reader subtitle support.
Version: {info.version}.
Copyright \u00a9 2022 mohamedSulaimanAlmarzooqi, mazen428
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
"""


class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="About")
        sizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.TextCtrl(
            self,
            value=about_text,
            style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2,
            size=(500, 500),
        )
        sizer.Add(text, 0, wx.ALL | wx.EXPAND, 10)
        link_sizer = wx.BoxSizer(wx.HORIZONTAL)
        link_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                label="Homepage",
                url="https://github.com/mediasplashapp/mediasplash",
            )
        )
        link_sizer.Add(wx.adv.HyperlinkCtrl(self, label="License", url="https://www.gnu.org/licenses/gpl-3.0.txt"))
        link_sizer.Add(
            wx.adv.HyperlinkCtrl(
                self,
                label="Donate",
                url="https://www.paypal.com/donate/?hosted_button_id=4M3SJPRA8AQUW",
            )
        )
        sizer.Add(link_sizer, 0, wx.ALL, 5)
        sizer.Add(wx.Button(self, wx.ID_CLOSE))
        self.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_CLOSE), id=wx.ID_CLOSE)
        self.SetSizer(sizer)
        self.SetEscapeId(wx.ID_CLOSE)
        sizer.Fit(self)
        self.Layout()
