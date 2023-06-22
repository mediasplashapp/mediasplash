# goto dialog
# Copyright (C) 2022 mohamedSulaimanAlmarzooqi, Mazen428
# a part of mediasplash.
# This program is free software:
#  you can redistribute it and/or modify it under the terms of the GNU General Public License 3.0 or later

# See the file LICENSE for more details.

import wx
import datetime


class GoToPositionPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        goto_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, "Go to Position")
        goto_box = goto_sizer.GetStaticBox()
        goto_sizer.Add(wx.StaticText(goto_box, label="Type a position to quickly go to, for example: 5.30"))
        self.text = wx.TextCtrl(goto_box)
        goto_sizer.Add(self.text, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(goto_sizer)


class ChaptersPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        chapters_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, "Go to chapter")
        goto_box = chapters_sizer.GetStaticBox()
        chapters_sizer.Add(wx.StaticText(goto_box, label="Select a chapter to go to"))
        self.list_ctrl = wx.ListCtrl(goto_box, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Title")
        self.list_ctrl.InsertColumn(1, "Start Time")
        chapters_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(chapters_sizer)

    def PopulateChapters(self, chapters):
        self.list_ctrl.DeleteAllItems()
        for idx, chapter in enumerate(chapters):
            self.list_ctrl.InsertItem(idx, chapter["title"])
            self.list_ctrl.SetItem(idx, 1, str(datetime.timedelta(seconds=round(chapter["time"]))))


class GoToDialog(wx.Dialog):
    def __init__(self, parent, chapters):
        super().__init__(parent, title="Go to")
        self.book = wx.Choicebook(self)
        position_page = GoToPositionPanel(self.book)
        self.book.AddPage(position_page, "Go to position")
        if chapters:
            chapters_page = ChaptersPanel(self.book)
            self.book.AddPage(chapters_page, "Go to chapter")
            chapters_page.PopulateChapters(chapters)
        else:
            chapters_page = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.book, 1, wx.ALL | wx.EXPAND, 10)

        # Add OK and Cancel buttons
        button_sizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.book.SetSelection(0)
        # Set the dialog size
        self.Fit()
        self.Layout()
        if chapters_page:
            chapters_page.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda event: wx.CallAfter(self.EndModal(wx.ID_OK)))
        position_page.text.SetFocus()

    def ShowModal(self):
        result = super().ShowModal()
        if result == wx.ID_OK:
            self.selection = self.book.GetSelection()
            page = self.book.GetCurrentPage()
            if self.selection == 0:
                self.dlg_value = page.text.GetValue()
            elif self.selection == 1:
                self.dlg_value = page.list_ctrl.GetFirstSelected()
        return result
