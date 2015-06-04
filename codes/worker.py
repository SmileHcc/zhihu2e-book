# -*- coding: utf-8 -*-

# ######################################################
# File Name   :    worker.py
# Description :    爬取网页的内容，保存到数据库中
# Author      :    Frank，SmileHcc
# Date        :    2014.04.14
# ######################################################

import threading

from codes.contentParse import *


class PageWorker(BaseClass, HttpBaseClass, SqlClass):
    def __init__(self, conn=None, urlInfo={}):
        self.conn = conn
        self.cursor = conn.cursor()
        self.maxPage = ''
        self.urlInfo = urlInfo
        self.maxThread = urlInfo['baseSetting']['maxThread']
        self.url = urlInfo['baseUrl']
        self.suffix = ''
        self.cookieJarInMemory = cookielib.LWPCookieJar
        self.addProperty()
        self.setCookie()
        self.setWorkSchedule()

    def getMaxPage(self, content):
        u"""
        Don't finding unicode char in normal string
        """
        try:
            pos = content.index('">下一页</a></span>')
            rightPos = content.rfind("</a>", 0, pos)
            leftPos = content.rfind(">", 0, rightPos)
            maxPage = int(content[leftPos+1:rightPos])
            print u"答案列表共计{}页".format(maxPage)
            return maxPage
        except:
            print u"答案列表共计1页"
            return 1

    def addProperty(self):
        # TODO self.urlInfo = urlInfo
        return

    def setCookie(self, account=''):
        self.cookieJarInMemory = cookielib.LWPCookieJar()
        if account == '':
            Var = self.cursor.execute("select cookieStr, recordDate from LoginRecord order by recordDate desc").fetchone()
        else:
            Var = self.cursor.execute("select cookieStr, recordDate from LoginRecord order by recordDate desc where account = `{}`".format(account)).fetchone()
        cookieStr = Var[0]
        self.loadCookJar(cookieStr)

        cookieStr = ''
        for cookie in self.cookieJarInMemory:
            cookieStr += cookie.name + '=' + cookie.value + ';'
        self.extraHeader = {
            'User-Agent':    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:34.0) Gecko/20100101 Firefox/34.0',
            'Referer':    'www.zhihu.com/',
            'Host':   'www.zhihu.com',
            'DNT':    '1',
            'Connection': 'keep-alive',
            'Cache-Control':  'max-age=0',
            'Accept-Language':    'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
            #'Accept-Encoding':    'gzip, deflate',mao si bu neng yong
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJarInMemory))
        urllib2.install_opener(self.opener)
        return

    def loadCookJar(self, content=""):
        u"""
        set cookieJar
        :param content:
        :return:
        """
        fileName = u'./loadCookieJarTempFile.txt'
        f = open(fileName, 'w')
        f.write(content)
        f.close()
        self.cookieJarInMemory.load(fileName)
        os.remove(fileName)
        return

    def setWorkSchedule(self):
        """
        获取私人收藏夹需要携带cookie登陆
        专栏不需要
        :return:
        """
        self.workSchedule = {}
        detectUrl = self.url + self.suffix + str(self.maxPage)
        content = self.getHttpContent(url=detectUrl, extraHeader=self.extraHeader)
        self.maxPage = self.getMaxPage(content)
        for i in range(self.maxPage):
            self.workSchedule[i] = self.url + self.suffix + str(i + 1)
        # print "debug:workSchedule:" + str(self.workSchedule)

    def commitSuccess(self):
        print "录入数据库成功！"
        return


class QuestionWorker(PageWorker):
    def start(self):
        self.complete = set()
        maxTry = self.maxTry
        while maxTry > 0 and len(self.workSchedule) > 0:
            self.leader()
            maxTry -= 1
        return

    def leader(self):
        threadPool = []
        self.questionInfoDictList = []
        self.answerDictList = []
        for key in self.workSchedule:
            threadPool.append(threading.Thread(target=self.worker, kwargs={'workNo': key}))
        threadsCount = len(threadPool)
        threadLiving = 2
        while threadsCount > 0 or threadLiving > 1:   # 线程的数量大于0，活动线程大于1
            bufLength = self.maxThread - threadLiving
            if bufLength > 0 and threadsCount > 0:
                while bufLength > 0 and threadsCount > 0:
                    threadPool[threadsCount - 1].start()
                    bufLength -= 1
                    threadsCount -= 1
                    time.sleep(0.1)
            else:
                print u'正在读取答案页面，还有{}/{}张页面等待读取'.format(len(self.workSchedule) - len(self.complete), len(self.workSchedule))
                time.sleep(1)
            threadLiving = threading.activeCount()

        for questionInfoDict in self.questionInfoDictList:
            self.save2DB(self.cursor, questionInfoDict, 'questionIDinQuestionDesc', 'QuestionInfo')
        for answerDict in self.answerDictList:
            self.save2DB(self.cursor, answerDict, 'answerHref', 'AnswerContent')
        self.conn.commit()
        self.commitSuccess()
        return

    def worker(self, workNo = 0):
        u"""
        worker只执行一次，待全部worker执行完毕后由调用函数决定哪些worker需要再次运行
        重复的次数由self.maxTry指定
        """
        if workNo in self.complete:
            return
        content = self.getHttpContent(url=self.workSchedule[workNo], extraHeader=self.extraHeader, timeout=self.waitFor)
        if content == '':
            return
        parse = ParseQuestion(content)
        questionInfoDictList, answerDictList = parse.getInfoDict()
        for questionInfoDict in questionInfoDictList:
            self.questionInfoDictList.append(questionInfoDict)
        for answerDict in answerDictList:
            self.answerDictList.append(answerDict)
        self.complete.add(workNo)
        return

    def addProperty(self):
        self.maxPage = 1
        self.suffix = '?sort=created&page='
        self.maxTry = 5
        self.waitFor = 5
        return

class AnswerWorker(PageWorker):
    def addProperty(self):
        self.maxPage = ''
        self.suffix = ''
        self.maxTry = 5    # 运行次数
        self.waitFor = 5
        self.answerDictList = []
        return

    def start(self):
        maxTry = self.maxTry
        while maxTry > 0 and not self.answerDictList:
            self.leader()
            maxTry -= 1
        return

    def leader(self):
        self.questionInfoDictList = []
        self.answerDictList = []
        self.worker()
        for questionInfoDict in self.questionInfoDictList:
            self.save2DB(self.cursor, questionInfoDict, 'questionIDinQuestionDesc', 'QuestionInfo')
        for answerDict in self.answerDictList:
            self.save2DB(self.cursor, answerDict, 'answerHref', 'AnswerContent')
        self.conn.commit()
        self.commitSuccess()
        return

    def worker(self):
        content = self.getHttpContent(url=self.url, extraHeader=self.extraHeader, timeout=self.waitFor)
        if content == '':
            return
        parse = ParseAnswer(content)
        questionInfoDictList, answerDictList = parse.getInfoDict()
        for questionInfoDict in questionInfoDictList:
            self.questionInfoDictList.append(questionInfoDict)
        for answerDict in answerDictList:
            self.answerDictList.append(answerDict)
        return


class AuthorWorker(PageWorker):
    """
    TODO
    """
    def start(self):
        self.complete = set()
        maxTry = self.maxTry
        while maxTry > 0 and len(self.workSchedule) > 0:
            self.leader()
            maxTry -= 1
        return

    def getIndexID(self):
        u"""
        用于为Topic，collection，userAgree添加Index
        """
        return

    def clearIndex(self):
        u"""
        用于在插入Index之前先清空Index表
        """
        return

    def addIndex(self, answerHref):
        u"""
        用于插入Index
        """
        return

    def leader(self):
        # clear index cache
        self.getIndexID()
        self.clearIndex()

        self.catchFrontInfo()
        threadPool = []
        self.questionInfoDictList = []
        self.answerDictList = []
        for key in self.workSchedule:
            threadPool.append(threading.Thread(target=self.worker, kwargs={'workNo': key}))
        threadsCount = len(threadPool)
        threadLiving = 2
        while (threadsCount > 0 or threadLiving > 1):
            bufLength = self.maxThread - threadLiving
            if bufLength > 0 and threadsCount > 0:
                while bufLength > 0 and threadsCount > 0:
                    threadPool[threadsCount - 1].start()
                    bufLength -= 1
                    threadsCount -= 1
                    time.sleep(0.1)
            else:
                print u'正在读取答案页面，还有{}/{}张页面等待读取'.format(len(self.workSchedule) - len(self.complete), len(self.workSchedule))
                time.sleep(1)
            threadLiving = threading.activeCount()
        for questionInfoDict in self.questionInfoDictList:
            self.save2DB(self.cursor, questionInfoDict, 'questionIDinQuestionDesc', 'QuestionInfo')
        for answerDict in self.answerDictList:
            self.save2DB(self.cursor, answerDict, 'answerHref', 's')
            self.addIndex(answerDict['answerHref'])
        self.conn.commit()
        print 'commit complete'
        return

    def catchFrontInfo(self):
        content = self.getHttpContent(url=self.urlInfo['infoUrl'], extraHeader=self.extraHeader, timeout = self.waitFor)
        if content == '':
            return
        parse = AuthorInfoParse(content)
        infoDict = parse.getInfoDict()
        self.save2DB(self.cursor, infoDict, 'authorID', 'AuthorInfo')
        return


    def worker(self, workNo=0):
        u"""
        worker只执行一次，待全部worker执行完毕后由调用函数决定哪些worker需要再次运行
        重复的次数由self.maxTry指定
        这样可以给知乎服务器留出生成页面缓存的时间
        """
        if workNo in self.complete:
            return
        content = self.getHttpContent(url=self.workSchedule[workNo], extraHeader=self.extraHeader, timeout = self.waitFor)
        if content == '':
            return
        parse = ParseAuthor(content)
        questionInfoDictList, answerDictList = parse.getInfoDict()
        for questionInfoDict in questionInfoDictList:
            self.questionInfoDictList.append(questionInfoDict)
        for answerDict in answerDictList:
            self.answerDictList.append(answerDict)
        self.complete.add(workNo)
        return

    def addProperty(self):
        self.maxPage = 1
        self.suffix = '/answers?order_by=vote_num&page='
        self.maxTry = 5
        self.waitFor = 5
        return

class TopicWorker(AuthorWorker):
    def getIndexID(self):
        topicMatch = re.search(r'(?<=www.zhihu.com/topic/)\d{8}', self.url)
        if topicMatch == None:
            print u'抱歉，没能在网址中匹配到话题ID'
            print u'输入的话题网址为：{}'.format(self.url)
            print u'程序无法继续运行，请检查网址是否正确后重试'
            exit()
        self.topicID = topicMatch.group(0)
        return self.topicID

    def clearIndex(self):
        self.getIndexID()
        self.cursor.execute('delete from TopicIndex where topicID = ?', [self.topicID,])
        self.conn.commit()
        return

    def addIndex(self, answerHref):
        self.cursor.execute('replace into TopicIndex (answerHref, topicID) values (?, ?)', [answerHref, self.topicID])
        return

    def catchFrontInfo(self):
        content = self.getHttpContent(url=self.urlInfo['infoUrl'], extraHeader=self.extraHeader, timeout = self.waitFor)
        if content == '':
            return
        parse = TopicInfoParse(content)
        infoDict = parse.getInfoDict()
        self.save2DB(self.cursor, infoDict, 'topicID', 'TopicInfo')
        return

    def worker(self, workNo=0):
        if workNo in self.complete:
            return
        content = self.getHttpContent(url=self.workSchedule[workNo], extraHeader=self.extraHeader, timeout=self.waitFor)
        if content == '':
            return
        parse = ParseTopic(content)
        questionInfoDictList, answerDictList = parse.getInfoDict()
        for questionInfoDict in questionInfoDictList:
            self.questionInfoDictList.append(questionInfoDict)
        for answerDict in answerDictList:
            self.answerDictList.append(answerDict)
        self.complete.add(workNo)
        return

    def addProperty(self):
        self.maxPage = 1
        self.suffix = '/top-answers?page='
        self.maxTry = 5
        self.waitFor = 5
        return

class CollectionWorker(AuthorWorker):
    def getIndexID(self):
        collectionMatch = re.search(r'(?<=www.zhihu.com/collection/)\d{8}', self.url)
        if collectionMatch == None:
            print u'抱歉，没能在网址中匹配到收藏夹ID'
            print u'输入的收藏夹网址为：{}'.format(self.url)
            print u'程序无法继续运行，请检查网址是否正确后重试'
            exit()
        self.collectionID = collectionMatch.group(0)
        return self.collectionID

    def addIndex(self, answerHref):
        self.cursor.execute('replace into CollectionIndex (answerHref, collectionID) values (?, ?)', [answerHref, self.collectionID])
        return

    def catchFrontInfo(self):
        content = self.getHttpContent(url=self.urlInfo['infoUrl'], extraHeader=self.extraHeader, timeout = self.waitFor)
        if content == '':
            return
        parse = CollectionInfoParse(content)
        infoDict = parse.getInfoDict()
        self.save2DB(self.cursor, infoDict, 'collectionID', 'CollectionInfo')
        return

    def worker(self, workNo=0):
        if workNo in self.complete:
            return
        content = self.getHttpContent(url=self.workSchedule[workNo], extraHeader=self.extraHeader, timeout=self.waitFor)
        if content == '':
            return
        parse = ParseCollection(content)
        questionInfoDictList, answerDictList = parse.getInfoDict()
        for questionInfoDict in questionInfoDictList:
            self.questionInfoDictList.append(questionInfoDict)
        for answerDict in answerDictList:
            self.answerDictList.append(answerDict)
        self.complete.add(workNo)
        return

    def addProperty(self):
        self.maxPage = 1
        self.suffix = '?page='
        self.maxTry = 5
        self.waitFor = 5
        return
"""
add other worker:
"""
