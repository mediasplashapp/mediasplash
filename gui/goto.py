# goto dialog
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.

import wx


class GoToPosition(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        gbox_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, "Go to position")
        gbox = gbox_sizer.GetStaticBox()
        gbox_sizer.Add(wx.StaticText(gbox, label="EXample"))
        self.text = wx.TextCtrl(gbox)
        gbox_sizer.Add(self.text, 0, wx.ALL | wx.EXPAND, 10)
