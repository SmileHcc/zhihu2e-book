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
        frame = MainFrame("Zhihu2ebook", (50, 60), (1000, 600))
        frame.Show()
        self.SetTopWindow(frame)
        return True


class MainFrame(wx.Frame):

    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        self.create_menu()       # 创建菜单
        self.create_tool_bar()   # 创建工具栏
        self.create_split_window()  # 创建左中右3个panel
        self.Centre()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()  # 菜单
        menu_setting = wx.Menu()
        menu_file = wx.Menu()
        menu_help = wx.Menu()
        menu_bar.Append(menu_file, u"文件")
        menu_bar.Append(menu_setting, u"设置")
        menu_bar.Append(menu_help, u"帮助")

        menu_file.Append(-1, u"新建", u"新建一个文件保存当前的ReadList")
        menu_file.Append(-1, u"打开", u"打开文件作为ReadList.txt")
        menu_file.Append(-1, u"保存", u"将当前的ReadList保存为文件")
        menu_file.Append(-1, u"另存为", u"将当前的ReadList另存为")
        menu_file.AppendSeparator()
        menu_file.Append(-1, u"导出", u"设置导出生成的epub文件的路径")

        menu_setting.Append(-1, u"重新登陆", u"重新输入账号密码")
        menu_setting.Append(-1, u"配置", u"重新输入配置信息")
        menu_setting.AppendSeparator()
        menu_setting.Append(-1, u"退出")

        menu_help.Append(-1, u"说明")

        self.SetMenuBar(menu_bar)
        # self.CreateStatusBar()
        # self.SetStatusText("V0.1")


    def create_tool_bar(self):
        tool_id = {
            'config': wx.NewId(),
            'import': wx.NewId()
        }
        tool_bar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_TEXT | wx.TB_HORZ_LAYOUT)
        quit = tool_bar.AddLabelTool(wx.ID_EXIT, u"退出", wx.Bitmap('images/32/quit.png'))
        config = tool_bar.AddLabelTool(tool_id['config'], u"配置", wx.Bitmap('images/32/setting.png'))
        tool_bar.AddSeparator()
        import_read_list = tool_bar.AddLabelTool(tool_id['import'], u"导入ReadList", wx.Bitmap('images/32/import.png'))
        tool_bar.Realize()

    def create_split_window(self):
        splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE)
        splitter.SetMinimumPaneSize(150)

        # 左侧面板
        left_panel_contain = wx.Panel(splitter, -1)
        vbox_left = wx.BoxSizer(wx.VERTICAL)
        left_panel = LeftPanel(left_panel_contain, -1)
        vbox_left.Add(left_panel, 1, wx.EXPAND)
        left_panel_contain.SetSizer(vbox_left)
        # 中分隔窗
        splitter1 = wx.SplitterWindow(splitter, -1, style=wx.SP_LIVE_UPDATE)
        splitter1.SetMinimumPaneSize(50)
        # 中间面板
        middle_panel_contain = wx.Panel(splitter1, -1)
        vbox_middle = wx.BoxSizer(wx.VERTICAL)
        middle_panel = MiddlePanel(middle_panel_contain, -1)
        # middle_panel.SetBackgroundColour('blue')
        vbox_middle.Add(middle_panel, 1, wx.EXPAND | wx.BOTTOM)
        middle_panel_contain.SetSizer(vbox_middle)
        # middle_panel_contain.SetBackgroundColour('black')
        # 右侧面板
        right_panel_contain = wx.Panel(splitter1, -1)
        vbox_right = wx.BoxSizer(wx.VERTICAL)
        right_panel = RightPanel(right_panel_contain, -1)
        vbox_right.Add(right_panel, 1, wx.EXPAND)
        right_panel_contain.SetSizer(vbox_right)
        # 设置分隔窗比例
        splitter.SplitVertically(left_panel_contain, splitter1, 150)
        splitter1.SplitVertically(middle_panel_contain, right_panel_contain, -150)
        self.Centre()

class LeftPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_NONE)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # for i in range(4):
        #     vbox.Add(wx.Button(self, -1, label="test"+"    ", size=(-1, 40)), 0, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(vbox)
        self.Show(True)


class MiddlePanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_NONE)
        vbox = wx.BoxSizer(wx.VERTICAL)
        read_list_contain = wx.Panel(self, -1)
        # read_list_contain.SetBackgroundColour('red')
        self.create_read_list(read_list_contain, u"一行表示是一本书，$符号可以区分章节：")
        vbox.Add(read_list_contain, 6, wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)

        # 增加确认，取消按钮
        operation_panel = wx.Panel(self, -1)
        self.create_operation(operation_panel)
        vbox.Add(operation_panel, 1, wx.EXPAND | wx.TOP, border=5)

        self.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def create_read_list(self, parent, title):
        """
        创建编辑ReadList的
        :param parent:  Panel
        :param title:   显示的标题
        :return:
        """
        vbox = wx.BoxSizer(wx.VERTICAL)
        title_text = wx.StaticText(parent, -1, label=title)
        edit_read_list = wx.TextCtrl(parent, -1, value='test', style=wx.TE_MULTILINE)
        vbox.Add(title_text, 1, wx.EXPAND)
        vbox.Add(edit_read_list, 11, wx.EXPAND | wx.BOTTOM)

        parent.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def create_operation(self, parent):
        """
        确认，取消的Button
        :param parent:
        :return:
        """
        grid_sizer = wx.GridSizer(rows=1, cols=2, hgap=1, vgap=5)
        cancel_button = wx.Button(parent, -1, label=u"取消")
        ok_button = wx.Button(parent, -1, label=u"确认")
        grid_sizer.Add(cancel_button, 0, wx.ALIGN_RIGHT)
        grid_sizer.Add(ok_button, 0)
        parent.SetSizer(grid_sizer)
        self.Centre()
        self.Show(True)

class RightPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_NONE)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # for i in range(4):
        #     vbox.Add(wx.Button(self, -1, label="test"+"    ", size=(-1, 40)), 0, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(vbox)
        self.Show(True)


def main():
    app = Zhihu2ebookGUI(False)
    app.MainLoop()

if __name__ == '__main__':
    main()


# def OnQuit(self, event):
    #     self.Close()
    #
    # def OnAbout(self, event):
    #     wx.MessageBox(u"Zhihu2ebook程序",
    #             u"关于Zhihu2ebook", wx.OK | wx.ICON_INFORMATION, self)