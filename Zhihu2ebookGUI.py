# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    Zhihu2ebookGUI.py
# Description :    GUI界面程序入口。实际入口是Main.py中的类Zhihu2ebook，
#                  程序主要的内容就是该类中的main方法。
# Author      :    Frank
# Date        :    2014.04.23
# ######################################################

import wx

TITEL = u"登陆"
USER = u"账号"
PWD = u"密码"
USR_LEN = 5
PWD_LEN = 6
BUTTON_OK = u"确认"
BUTTON_CANCLE = u"取消"
TOP_TIP = u"请输入账号和密码"
DFAULT_USR = u"请输入真实的邮箱"
DEFAULT_PWD = u"请输入 6-128 位的密码"


class Zhihu2ebookGUI(wx.App):

    def OnInit(self):
        frame = MyFrame("Zhihu2ebook", (50, 60), (450, 340))
        frame.Show()
        self.SetTopWindow(frame)
        return True

class MyFrame(wx.Frame):

    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        menuFile = wx.Menu()
        menuFile.Append(1, u"关于...")
        menuFile.AppendSeparator()
        menuFile.Append(2, u"退出")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, u"设置")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        self.SetStatusText("V0.1")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=1)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=2)

    def OnQuit(self, event):
        self.Close()

    def OnAbout(self, event):
        wx.MessageBox(u"Zhihu2ebook程序",
                u"关于Zhihu2ebook", wx.OK | wx.ICON_INFORMATION, self)

def main():
    app = Zhihu2ebookGUI(False)
    app.MainLoop()

if __name__ == '__main__':
    main()
