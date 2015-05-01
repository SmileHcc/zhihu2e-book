# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    epubBuilder
# Description :    接收contentPackage的内容，输出电子书
# Author      :    Frank
# Date        :    2014.04.30
# ######################################################


from codes.epubBuilder.dict2Html import *
from codes.epubBuilder.imgDownloader import *
from codes.epubBuilder.epub import *


class Zhihu2Epub():
    u"""
    提供将Question-Answer格式的数据转换为电子书的功能
    """
    def __init__(self, contentPackage):
        self.package = contentPackage
        self.imgSet = set()                 # 用于储存图片地址，便于下载
        self.trans = dict2Html(contentPackage)

        self.kindDict = {
                'question': u'问题',
                'answer': u'问答',
                'topic': u'话题',
                'collection': u'收藏夹',
                'table': u'圆桌',
                'author': u'作者',
                'column': u'专栏',
                'article': u'文章',
                'merge': u'合并',
                }
        self.basePath = './tempSourceRepository/'
        self.targetPath = './books/'
        self.baseImgPath = './imgPool/'
        self.baseContentPath = './cacheRepo/'

        self.initBasePath()
        self.info2Title()
        self.trans2Tree()
        self.imgDownload()
        self.epubCreator()
        return

    def initBasePath(self):
        mkdir(self.targetPath)
        mkdir(self.basePath)
        chdir(self.basePath)
        mkdir(self.baseImgPath)
        rmdir(self.baseContentPath)
        mkdir(self.baseContentPath)
        return

    def trans2Tree(self):
        u"""
        将电子书内容转换为一系列文件夹+html网页
        :return:
        """
        self.contentList = self.trans.getResult()
        self.imgSet = self.trans.getImgSet()
        for content in self.contentList:
            fileIndex = self.baseContentPath + content['fileName'] + '.html'
            htmlFile = open(fileIndex, 'wb')
            htmlFile.write(content['fileContent'])
            htmlFile.close()
        return

    def info2Title(self):
        self.fileTitle = u'{kind}_{title}({ID})_知乎回答集锦'.format(kind=self.kindDict[self.package['kind']], title=self.package['title'], ID=self.package['ID'])
        illegalCharList = ['\\', '/', ':', '*', '?', '<', '>', '|', '"']
        for illegalChar in illegalCharList:
            self.fileTitle = self.fileTitle.replace(illegalChar, '')
        return

    def imgDownload(self):
        downloader = ImgDownloader(targetDir=self.baseImgPath, imgSet=self.imgSet)
        self.downloadedImgSet = downloader.leader()
        return

    def epubCreator(self):
        book = Book(self.fileTitle, '27149527')
        for content in self.contentList:
            htmlSrc = '../../' + self.baseContentPath + content['fileName'] + '.html'
            title = content['contentName']
            book.addHtml(src=htmlSrc, title=title)
        for src in self.downloadedImgSet:
            imgSrc = '../../' + self.baseImgPath + src
            if src == '':
                continue
            book.addImg(imgSrc)
        # 增加一些属性
        book.addLanguage('zh-cn')
        book.addCreator('Zhihu2ebook')
        book.addDesc(u'该电子书由Zhihu2ebook生成，软件工程课程设计，只是为了学习和练习XD')
        book.addRight('CC')
        book.addPublisher('Zhihu2ebook')
        book.addCss(u'../../../epubResource/markdownStyle.css')
        book.addCss(u'../../../epubResource/userDefine.css')

        print u'开始制作电子书'
        book.buildingEpub()
        return
