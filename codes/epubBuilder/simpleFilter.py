# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    simpleFilter.py
# Description :    负责查询所有数据
# Author      :    Frank
# Date        :    2014.04.15
# ######################################################

import re
import datetime

from codes.contentPackage import *


class BaseFilter(BaseClass):
    u"""
    Filter负责从数据库中查询出所有的数据
    Package进行数据的保存
    由其他的中间件负责将保存下来的数据转换成HTML代码 TODO
    """
    def __init__(self, cursor=None,urlInfo={}):
        self.imgBasePath = '../img/'
        self.cursor = cursor
        self.urlInfo = urlInfo
        self.picQuality = urlInfo['baseSetting']['picQuality']
        self.package = ContentPackage()
        self.addProperty()
        return

    def addProperty(self):
        """
        增加属性，子类实现
        :return:
        """
        return

    def authorLogoFix(self, imgHref=''):
        # 头像用大图  TODO
        imgHref = re.sub(r'_..jpg', '', imgHref, 1)
        if imgHref:
            imgHref += '_b.jpg'
        return u'<div class="duokan-image-single"><img src="{}" alt=""/></div>'.format(imgHref)

    def contentImgFix(self, content='', imgQuality=1):
        if imgQuality == 0:
            content = self.removeTag(content, ['img', 'noscript'])
        else:
            # 将writedot.jpg替换为正常图片
            content = self.removeTag(content, ['noscript'])
            for imgTag in re.findall(r'<img.*?>', content):
                try:
                    imgTag.index('misc/whitedot.jpg')  # ???TODO
                except:
                    imgContent = imgTag.replace('data-rawwidth', 'width')
                    imgContent = self.removeTagAttribute(imgContent, ['class'])
                    content = content.replace(imgTag, imgContent)
                else:
                    content = content.replace(imgTag, '')

            # 抽取它的src属性，直接手工新写一个img标签 # ??? TODO
            if imgQuality == 1:
                for imgTag in re.findall(r'<img.*?>', content):
                    imgContent = self.trimImg(imgTag)
                    content = content.replace(imgTag, self.fixPic(imgContent))
            else:
                for imgTag in re.findall(r'<img.*?>', content):
                    try:
                        imgTag.index('data-original')
                    except ValueError:
                        # 所考虑的这种情况存在吗？存疑
                        content = content.replace(imgTag, self.fixPic(self.trimImg(imgTag)))
                    else:
                        # 将data-original替换为src即为原图
                        imgContent = self.removeTagAttribute(imgTag, ['src']).replace('data-original', 'src')
                        imgContent = self.trimImg(imgContent)
                        content = content.replace(imgTag, self.fixPic(imgContent))
        return content

    def trimImg(self, imgContent=''):
        src = re.search(r'(?<=src=").*?(?=")', imgContent)
        if src != None:
            src = src.group(0)
            if src.replace(' ', '') != '':
                    return '<img src="{}" alt="">'.format(src)
        return ''

    def fixPic(self, imgTagContent=''):
        return '\n<div class="duokan-image-single">\n{}\n</div>\n'.format(imgTagContent)

    def removeTagAttribute(self, tagContent='', removeAttrList=[]):
        for attr in removeAttrList:
            for attrStr in re.findall(r'\s' + attr + '[^\s>]*', tagContent):
                tagContent = tagContent.replace(attrStr, '')
        return tagContent

    def removeTag(self, text='', tagname=[]):
        for tag in tagname:
            text = text.replace('</'+tag+'>', '')
            text = re.sub(r"<" + tag + r'.*?>', '', text)
        return text

    def getFileName(self, imgHref=''):
        return imgHref.split('/')[-1]

    def str2Date(self, date=''):
        return datetime.datetime.strptime(date, '%Y-%m-%d')


class QuestionFilter(BaseFilter):
    u"""
    每次运行Filter生成一本书
    TODO，每个章节加个封面
    """
    def addProperty(self):
        self.questionID = self.urlInfo['questionID']
        return

    def initQuestionPackage(self, questionID = ''):
        print "initQuestionPackage???"
        sql = '''select
                questionIDinQuestionDesc         as questionID,
                questionCommentCount             as commentCount,
                questionFollowCount              as followCount,
                questionAnswerCount              as answerCount,
                questionViewCount                as viewCount,
                questionTitle                    as questionTitle,
                questionDesc                     as questionDesc
                from QuestionInfo where questionIDinQuestionDesc = ? '''
        bufDict = self.cursor.execute(sql, [questionID,]).fetchone()
        # print "initQuestionPackage???"
        questionInfo = {}
        questionInfo['kind'] = 'question'
        questionInfo['questionID'] = bufDict[0]
        questionInfo['commentCount'] = bufDict[1]
        questionInfo['followerCount'] = bufDict[2]
        questionInfo['answerCount'] = bufDict[3]
        questionInfo['viewCount'] = bufDict[4]
        questionInfo['title'] = bufDict[5]
        print "here?:"
        print bufDict[6]
        questionInfo['description'] = self.contentImgFix(bufDict[6], self.picQuality)
        print "not here"
        print u"debug:simpleFilter中，questionInfo['description']是"
        # print questionInfo['description']

        package = QuestionPackage()
        package.setPackage(questionInfo)
        return package

    def addAnswerTo(self, questionPackage, answerHref=''):
        questionID = questionPackage['questionID']
        baseSql = '''select
                            authorID,
                            authorSign,
                            authorLogo,
                            authorName,
                            answerAgreeCount,
                            answerContent,
                            questionID,
                            answerID,
                            commitDate,
                            updateDate,
                            answerCommentCount,
                            noRecordFlag,
                            answerHref
                        from AnswerContent where noRecordFlag = 0 '''
        if answerHref:
            sql = baseSql + '''and answerHref = ?'''
            bufList = self.cursor.execute(sql, [answerHref]).fetchall()
        else:    # TODO 5???
            sql = baseSql + '''and questionID = ? and answerAgreeCount > 5'''
            bufList = self.cursor.execute(sql, [questionID,]).fetchall()

        for answer in bufList:
            package = AnswerPackage()
            answerDict = {}
            answerDict['authorID'] = answer[0]
            answerDict['authorSign'] = answer[1]
            answerDict['authorLogo'] = self.authorLogoFix(answer[2])
            answerDict['authorName'] = answer[3]
            answerDict['agreeCount'] = int(answer[4])
            answerDict['content'] = self.contentImgFix(answer[5], self.picQuality)
            answerDict['questionID'] = answer[6]
            answerDict['answerID'] = answer[7]
            answerDict['updateDate'] = self.str2Date(answer[9])
            answerDict['commentCount'] = int(answer[10])

            package.setPackage(answerDict)
            questionPackage.addAnswer(package)

        return questionPackage

    def addInfo(self):
        u"""
        问题信息
        """
        sql = '''select
                questionIDinQuestionDesc as questionID,
                questionCommentCount     as commentCount,
                questionFollowCount      as followCount,
                questionAnswerCount      as answerCount,
                questionViewCount        as viewCount,
                questionTitle            as questionTitle,
                questionDesc             as questionDesc
                from QuestionInfo where questionIDinQuestionDesc = ? '''
        result = self.cursor.execute(sql, [self.questionID,]).fetchone()
        infoDict = {}
        infoDict['ID'] = self.questionID
        infoDict['kind'] = 'question'
        infoDict['title'] = result[5]
        infoDict['description'] = result[6]
        infoDict['followerCount'] = result[2]
        infoDict['commentCount'] = result[1]

        self.package.setPackage(infoDict)
        return

    def getResult(self):
        print "test1"
        questionPackage = self.initQuestionPackage(self.questionID)
        print "test2"
        questionPackage = self.addAnswerTo(questionPackage)

        print "DEBUG:QuestionFilter,self.questionPackage"
        # print questionPackage

        self.package.addQuestion(questionPackage)
        self.addInfo()
        print "DEBUG:QuestionFilter,self.package?"
        # print self.package
        return self.package


class AnswerFilter(QuestionFilter):
    def addProperty(self):
        self.questionID = self.urlInfo['questionID']
        self.answerID = self.urlInfo['answerID']
        return

    def createAnswerHref(self, questionID, answerID):
        return 'http://www.zhihu.com/question/{0}/answer/{1}'.format(questionID, answerID)

    def getResult(self):
        questionPackage = self.initQuestionPackage(self.questionID)
        answerHref = self.createAnswerHref(self.questionID, self.answerID)
        questionPackage = self.addAnswerTo(questionPackage, answerHref)

        self.package.addQuestion(questionPackage)
        self.addInfo()
        return self.package
