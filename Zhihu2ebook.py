# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    Zhihu2ebook.py
# Description :    程序的主入口。实际入口是Main.py中的类Zhihu2ebook，
#                  程序主要的内容就是该类中的main方法。
# Author      :    Frank
# Date        :    2014.03.04
# ######################################################


import sys
reload(sys)
# 修改系统（终端输出）默认的编码，文件格式、处理格式
sys.setdefaultencoding('utf-8')

# f = open('log.txt', 'w')
old_stdout = sys.stdout
# sys.stdout = f

from codes.main import *

gameBegin = Zhihu2ebook()
gameBegin.main_start()

sys.stdout = old_stdout
# f.close()
print 'It\'s done'
# print sys.getdefaultencoding()

