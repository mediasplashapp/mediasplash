import wx


class ClearableMenu(wx.Menu):
    def Clear(self):
        items = self.GetMenuItems()
        for i in items:
            self.DestroyItem(i.GetId())

    def GetChecked(self):
        items = self.GetMenuItems()
        for i in items:
            if i.IsChecked():
                return i
