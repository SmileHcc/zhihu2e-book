# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    dict2Html.py
# Description :
# Author      :    Frank
# Date        :    2014.04.30
# ######################################################

import re

from codes.epubBuilder.htmlTemplate import *


class dict2Html():
    def __init__(self, contentPackage):
        self.trans = AgreeCountTransfer(contentPackage)  # TODO 专栏
        return

    def getResult(self):
        return self.trans.getResult()

    def getImgSet(self):
        return self.trans.getImgSet()


class Transfer():
    u"""
    基本的转换类，提供通用的字典转Html方法
    """
    def __init__(self, contentPackage):
        self.package = contentPackage
        self.imgSet = set()
        self.htmlList = []
        self.contentList = []
        self.questionList = []
        return

    def imgFix(self, content):
        for imgTag in re.findall(r'<img.*?>', content):
            src = re.search(r'(?<=src=").*?(?=")', imgTag)
            if src is None:
                continue
            else:
                src = src.group(0)
                if src.replace(' ', '') == '':
                    continue
            self.imgSet.add(src)
            fileName = self.getFileName(src)
            content = content.replace(src, '../images/' + fileName)
        return content

    def getFileName(self, imgHref=''):
        return imgHref.split('/')[-1]

    def authorLink(self, authorName, authorID):
        return "<a href='http://www.zhihu.com/people/{0}'>{1}</a>".format(authorID, authorName)

    def getImgSet(self):
        return self.imgSet

    def contentTrans(self):
        """
        TODO 未完成
        :return:
        """
        print "contentTrans??111"
        for question in self.questionList:
            print "contentTrans??"

            contentHeader = {}
            for key in ['titleImage', 'titleName', 'titleDesc', 'titleCommentCount']:
                contentHeader[key] = ''

            contentHeader['titleName'] = question['title']
            if question['kind'] == 'article':      # TODO
                contentHeader['titleImage'] = '<div class="duokan-image-single"><img src="{}" alt=""/></div>'.format(question['titleLogo'])
            else:
                contentHeader['titileDesc'] = question['description']
                contentHeader['titleCommentCount'] = '评论数:{}'.format(question['commentCount'])
            content = {}
            content['contentHeader'] = contentHeaderTemplate(contentHeader)
            content['contentBody'] = ''
            content['contentFooter'] = ''

            for answer in question['answerList']:
                contentBody = {}

                for key in ['authorLogo', 'authorName', 'authorSign', 'content', 'agreeCount', 'commentCount', 'updateDate']:
                    contentHeader[key] = ''

                contentBody['authorLogo'] = self.imgFix(answer['authorLogo'])
                contentBody['authorName'] = self.authorLink(answer['authorName'], answer['authorID'])
                contentBody['authorSign'] = '&nbsp;&nbsp;&nbsp;' + answer['authorSign']
                contentBody['content'] = self.imgFix(answer['content'])
                contentBody['agreeCount'] = '赞同数:{}'.format(answer['agreeCount'])
                contentBody['commentCount'] = '评论数:{}'.format(answer['commentCount'])
                contentBody['updateDate'] = '更新日期:{}'.format(answer['updateDate'].strftime('%Y-%m-%d'))

                content['contentBody'] += contentBodyTemplate(contentBody)

            htmlContent = contentTemplate(content)
            htmlContent = structTemplate({'leftColumn': '', 'middleColumn': htmlContent, 'rightColumn': ''})
            htmlContent = baseTemplate({
                              'Title': question['title'],
                              'Header': '',
                              'Body': htmlContent,
                              'Footer': '',
                          })
            # TODO
            buf = {'fileName': str(question['questionID']), 'contentName': question['title'], 'fileContent': htmlContent}
            self.contentList.append(buf)
        return self.contentList

    def infoPageTrans(self):
        """
        TODO   未完成
        :return:
        """
        content = {}
        content['title'] = self.package['title']
        content['copyRight'] = u'此处应有版权声明'
        htmlContent = infoPageTemplate(content)
        htmlContent = structTemplate({'leftColumn': '', 'middleColumn': htmlContent, 'rightColumn': ''})
        htmlContent = baseTemplate({
                          'Title': self.package['title'],
                          'Header': '',
                          'Body': htmlContent,
                          'Footer': '',
                      })
        buf = {'fileName': 'infoPage', 'contentName': self.package['title'], 'fileContent': htmlContent}
        self.contentList.insert(0, buf)
        return self.contentList

    def getResult(self):
        self.initQuestionList()   # TODO
        self.infoPageTrans()
        self.contentTrans()
        return self.contentList


class UpdateDateTransfer(Transfer):
    def initQuestionList(self):
        self.questionList = self.package.format_sortBy_updateDate_asc()
        return



class AgreeCountTransfer(Transfer):
    def initQuestionList(self):
        self.questionList = self.package.format_sortBy_agree_desc()




