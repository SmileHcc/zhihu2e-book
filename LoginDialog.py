# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    LoginDialog.py
# Description :    Login窗体
# Author      :    Frank
# Date        :    2014.04.23
# ######################################################

TITLE = u"登陆"
USER = u"账号"
PWD = u"密码"
USR_LEN = 5
PWD_LEN = 6
BUTTON_OK = u"确认"
BUTTON_CANCEL = u"取消"
TOP_TIP = u"请输入知乎网站的账号和密码"
DEFAULT_USR = u"请输入真实的邮箱"
DEFAULT_PWD = u"请输入 6-128 位的密码"

import wx
import re

class LoginDialog(wx.Dialog):
    u"""
    登陆对话窗体,请勿直接调用ShowModal() ,调用Show()
    """

    def __init__(self, parent=None, title=TITLE, size=(300, 220), user_len=USR_LEN, pwd_len=PWD_LEN):
        wx.Dialog.__init__(self, parent, -1, title, size=size, style=wx.DEFAULT_DIALOG_STYLE)
        self.txtCtrMap = {}           # 缓存输入框
        self.okBtn = None
        self.pwdLen = pwd_len
        self.usrLen = user_len
        self.create_component()

    # 构建label项
    def _data_txt_label(self):
        return ((USER, 0, self._on_user_txt_input, DEFAULT_USR),
                (PWD, wx.TE_PASSWORD, self._on_pwd_input, DEFAULT_PWD))

    # 构建button项
    def _data_with_button(self):
        return (wx.ID_OK, BUTTON_OK), (wx.ID_CANCEL, BUTTON_CANCEL)

    # 构建TextCtrl项
    def _create_txt_label(self, sizer, each_label, each_style, each_handler, dvalue):
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, each_label)
        box.Add(label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        text = wx.TextCtrl(self, -1, dvalue, size=(150, -1), style=each_style)
        text.Bind(wx.EVT_TEXT, each_handler)
        box.Add(text, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.txtCtrMap[each_label] = text

    def _create_button(self, btn_sizer, eachID, each_label):
        btn = wx.Button(self, eachID, each_label)
        if eachID == wx.ID_OK:
            btn.SetDefault()
            self.okBtn = btn
            btn.Disable()
        btn_sizer.AddButton(btn)

    # 根据数据项构建组建
    def create_component(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top_tip = wx.StaticText(self, -1, TOP_TIP)
        sizer.Add(top_tip, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        for eachLabel, eachStyle, eachHandler, dvalue in self._data_txt_label():
            self._create_txt_label(sizer, eachLabel, eachStyle, eachHandler, dvalue)
        btn_sizer = wx.StdDialogButtonSizer()
        for eachID, eachLabel in self._data_with_button():
            self._create_button(btn_sizer, eachID, eachLabel)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.SetSizer(sizer)

    def _on_user_txt_input(self, event):
        self.ok_button()

    def _on_pwd_input(self, event):
        self.ok_button()

    # 账号是邮箱，密码大于等于6位
    def ok_button(self):
        self.okBtn.Enable()
        usr_str = self.txtCtrMap[USER].GetValue()
        pwd_str = self.txtCtrMap[PWD].GetValue()
        if re.search(r'\w+@[\w\.]{3,}', usr_str) is None or len(pwd_str) < self.pwdLen:
            self.okBtn.Disable()

    # 调用该函数将显示窗体并确定后可返回结果
    def Show(self):
        res = self.ShowModal()
        if res == wx.ID_OK:
            return self.txtCtrMap[USER].GetValue(), self.txtCtrMap[PWD].GetValue()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    log = LoginDialog()
    res = log.Show()
    print res
    log.Destroy()
    app.MainLoop()
