# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    contentPackage.py
# Description :    保存从Filter取出的数据
# Author      :    Frank
# Date        :    2014.04.10
# ######################################################

from baseclass import *

class Package(BaseClass):
    u"""
    Package的基础类
    用来保存从Filter取出的数据
    TODO 取出的数据再打一层包
    """
    def __init__(self):
        self.package = {}
        self.initPackage()
        return

    def initPackage(self):
        return

    def setPackage(self, dataDict):
        for key in dataDict:
            self.package[key] = dataDict[key]
        return

    def getResult(self):
        return self.package

    # 重载[]与[] =操作符  TODO 为什么要重载
    def __getitem__(self, key):    # 返回键对应的值
        return self.package[key]

    def __setitem__(self, key, val):    # 设置给定键的值
        return self.package.__setitem__(key, val)


class ContentPackage(Package):
    u'''
    字典结构
    *   creatorID
    *   creatorSign
    *   creatorName
    *   creatorLogo
    *   ID   专栏/话题/收藏夹的ID
    *   kind 类别（专栏/话题/收藏夹/问题合集）
    *   title
    *   logo
    *   description
    *   followerCount
    *   commentCount
    *   contentCount  文章总数/答案总数/问题总数等
    *   extraKey  留作日后扩展
    *   questionDict  用于存储问题内容/专栏文章内容
        *   以[question_{questionID}或{columnID}_{articleID}]为key值
    '''
    def initPackage(self):
        self.package['creatorID'] = ''
        self.package['creatorSign'] = ''
        self.package['creatorName'] = ''
        self.package['creatorLogo'] = ''
        self.package['ID'] = ''
        self.package['kind'] = ''
        self.package['title'] = ''
        self.package['logo'] = ''
        self.package['description'] = ''
        self.package['followerCount'] = 0
        self.package['commentCount'] = 0
        self.package['followerCount'] = 0
        self.package['contentCount'] = 0
        self.package['extraKey'] = {}
        self.package['questionDict'] = {}

        self.questionDict = self.package['questionDict']

        # TODO


class QuestionPackage(Package):
    u'''
    专栏文章和问题的kind要分开
    其ID命名规则为
    问题ID为"question_{questionID}".format(questionID)
    专栏ID为"{columnID}_{articleID}".format(columnID, articleID)
    其中titleLogo项专为专栏文章使用
    字典结构:
    *   Question
        *   questionID
        *   kind
        *   title
        *   titleLogo
        *   description
        *   updateDate
        *   commentCount
        *   followerCount
        *   viewCount
        *   answerCount
        *   agreeCount    赞同数总和，方便排序
        *   extraKey      留作日后扩展
        *   answerDict    存储答案内容，使用answerID/articleID做key
    '''
    def initPackage(self):
        self.package['questionID'] = ''
        self.package['kind'] = ''
        self.package['title'] = ''
        self.package['titleLogo'] = ''
        self.package['description'] = ''
        self.package['updateDate'] = ''
        self.package['commentCount'] = 0
        self.package['viewCount'] = 0
        self.package['answerCount'] = 0
        self.package['followerCount'] = 0
        self.package['extraKey'] = {}
        self.package['answerDict'] = {}
        self.answerDict = self.package['answerDict']
        def addAnswer(self, answerPackage):
            u'''
            answer中没有多少需要合并的信息，所以不对answer调用merge方法
            '''
            answerID = answerPackage['answerID']
            if not answerID in self.answerDict:
                self.answerDict[answerID] = answerPackage
            return

        def merge(self, questionPackage):
            if questionPackage['kind'] != self.package['kind']:
              return
            for key in ['title', 'titleLogo', 'description', 'updateDate']:
                if questionPackage[key] != '':
                    self.package[key] = questionPackage[key]

            for key in questionPackage['answerDict']:
                self.addAnswer(questionPackage['answerDict'][key])
        return

    def getResult(self):
        self.package['answerCount'] = len(self.answerDict)
        agreeCount = 0
        for key in self.answerDict:
            agreeCount += self.answerDict[key]['agreeCount']
        self.package['agreeCount'] = agreeCount
        return self.package

class AnswerPackage(Package):
    u'''
    数据结构
    其中，对于Article而言，questionID即为columnID,answerID即为articleID
    *   Answer
        *   authorID
        *   authorSign
        *   authorLogo
        *   authorName
        *   questionID
        *   answerID
        *   content
        *   updateDate
        *   agreeCount
        *   commentCount
        *   collectCount
        *   extraKey
            *   留作日后扩展
    '''
    def initPackage(self):
        self.package['authorID']     = ''
        self.package['authorSign']   = ''
        self.package['authorLogo']   = ''
        self.package['authorName']   = ''
        self.package['questionID']   = ''
        self.package['answerID']     = ''
        self.package['content']      = ''
        self.package['updateDate']   = ''
        self.package['agreeCount']   = 0
        self.package['commentCount'] = 0
        self.package['collectCount'] = 0
        self.package['extraKey']     = {}
        return