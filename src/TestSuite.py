from bootstrap import *
import requests
import json
import time
import xlsxwriter
from web_socket import WebSocketClient
from datetime import datetime
from tqdm import tqdm
import re
import TestUtil
from pymongo import MongoClient


class TestSuite(object):

    def __init__(self, name,input,fileName):
        self._name = name
        self.result = {}
        self.botName = None
        self.botId = None
        self.testCases = []
        self.index = 2
        self.format = None
        self.bot = None
        self.discardMessage = None
        self.input = input
        self.fileName =fileName

    def begin(self):
        self.__loadTestCases()
        return self.__start()

    def result(self):
        return self.result

    def __loadTestCases(self):
        testCases = []
        data = {}
        #client = MongoClient('localhost', 27017)
        #mydatabase = client['test_cases']
        #cursor = mydatabase.myTable.find()
        for key in self.input.keys():
            test_case = {
                "discardBefore": True,
                "name": str(key),
                "messages": self.input[key]
            }
            testCases.append(test_case)
        self.botName = "Morgan Stanley POC"
        self.botId = "st-b334e88c-9b70-5012-8298-eecb3af5dc2d"
        self.testCases = testCases
        self.welcomeMessageCount = int(data.get("welcomeMessageCount", 0))
        self.discardMessage = data.get("discardMessage", "discard all")

    def __start(self):
        self.bot = self.__startConnection()
        now = datetime.now()
       # fileName = 'TestResults/'+self._name+ str(now.replace(microsecond=0)) +'.xlsx'
        #fileName = 'TestResults/' + self._name + '.xlsx'
        fileName = self.fileName
        workbook = xlsxwriter.Workbook(fileName)
        worksheet = workbook.add_worksheet()
        worksheet2 = workbook.add_worksheet()
        self.format = workbook.add_format()
        self.format.set_text_wrap()
        self.countpass = 0
        self.countfail = 0
        self.total = 0

        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', "ConversationId", bold)
        worksheet.write('B1', "Input", bold)
        worksheet.write('C1', "Actual", bold)
        worksheet.write('D1', "Expected", bold)
        worksheet.write('E1', "ResultType", bold)
        worksheet.write('F1', "SequenceId", bold)
        worksheet2.write('A1', "Pass", bold)
        worksheet2.write('B1', "Fail", bold)
        worksheet2.write('C1', "Total", bold)
        worksheet2.write('D1', "Coverage", bold)
        start = datetime.now()

        for testCase in tqdm(self.testCases):
            try:
                diff = datetime.now() - start
                if diff.seconds > 300:
                    self.bot = self.__reconnect()
                    start = datetime.now()
                self.__executeTestCase(testCase, worksheet, worksheet2)
            except Exception as e:
                print("Exception")
                print(e)
            time.sleep(1)
        self.bot.close()
        workbook.close()
        return self.countpass, self.countfail

    def __executeTestCase(self, testCase, worksheet, worksheet2, iter=0):
        sequenceCount =0
        discardBefore = testCase.get("discardBefore", False)
        if discardBefore:
            responses = self.bot.sendMessage(self.discardMessage, 1)
            if responses and len(responses) == 1:  # and "discarding the task for now" in responses[0].lower():
                iter = 0
                pass
            else:
                if iter == 0:
                    self.__executeTestCase(testCase, worksheet, worksheet2, iter + 1)
                    return
        worksheet.write('A' + str(self.index), testCase["name"])
        payload_map={}
        for message in testCase["messages"]:
            sequenceCount = sequenceCount +1
            outputs = message["outputs"]
            input= message["input"]
            input_lower = input.replace(' ','').lower()
            if payload_map.get(input_lower) is not None:
                input = payload_map.get(input_lower)
            responses = self.bot.sendMessage(input, len(outputs))
            payload_map={}
            worksheet.write('B' + str(self.index), message["input"])

            if len(responses) != len(outputs):
                self.bot = self.__reconnect()
                if iter == 1:
                    worksheet.write('E' + str(self.index), "FN", self.format)
                    self.countfail += 1
                    worksheet2.write('B2', self.countfail)
                    worksheet2.write('C2', self.countpass + self.countfail)
                    worksheet.write('C' + str(self.index), str(responses), self.format)
                    worksheet.write('D' + str(self.index), str(outputs), self.format)
                    self.index = self.index + 1
                    return
                else:
                    self.__executeTestCase(testCase, worksheet, worksheet2, iter + 1)
                    return
            for i in range(len(responses)):
                success = True
                messageObj = responses[i]
                response, component, payload_map = TestUtil.componentToText(messageObj)
                if isinstance(outputs[i], dict):
                    eqCondition = False
                    containsObj = outputs[i].get("contains", None)
                    if not containsObj:
                        containsObj = outputs[i].get("equals", None)
                        eqCondition = True

                    if isinstance(containsObj, dict):
                        containsStr = str(containsObj)
                        allOf = False
                        matches = []
                        expMatches = containsObj.get("oneOf", None)
                        if not expMatches:
                            expMatches = containsObj.get("allOf", None)
                            allOf = True
                        for expMatch in expMatches:
                            if eqCondition:
                                if expMatch.lower() == response.lower():
                                    pass
                                else:
                                    matches.append(False)
                            else:
                                if TestUtil.validateContains(response.lower(), expMatch.lower()):
                                    matches.append(True)
                                else:
                                    matches.append(False)
                        if allOf and False in matches:
                            success = False
                        elif True not in matches:
                            success = False

                    else:
                        containsStr = containsObj
                        if not TestUtil.validateContains(response.lower(), containsStr.lower()):
                            debug.info("User Input::" + message["input"] + ",TestCase:" + testCase[
                                "name"] + " Failed,Actual: " + response + ",Expected: " + containsStr)
                            success = False

                else:
                    containsStr = outputs[i]
                    if response != outputs[i]:
                        debug.info("else User Input::" + message["input"] + ",TestCase:" + testCase[
                            "name"] + " Failed,actual:" + response + " expected:" + outputs[i])
                        success = False
                if not success:
                    worksheet.write('E' + str(self.index), "FN", self.format)
                    self.countfail += 1
                    worksheet2.write('B2', self.countfail)
                    worksheet2.write('C2', self.countpass + self.countfail)
                    worksheet2.write('D2', (self.countpass / (self.countpass + self.countfail)) * 100)
                    worksheet.write('C' + str(self.index), response + "", self.format)
                    worksheet.write('D' + str(self.index), containsStr + "", self.format)
                    worksheet.write('F' + str(self.index), str(sequenceCount), self.format)
                    self.index = self.index + 1
                    return
                response = response[:-1]
                worksheet.write('C' + str(self.index), response + "", self.format)
                worksheet.write('D' + str(self.index), containsStr + "", self.format)
                worksheet.write('F' + str(self.index), str(sequenceCount), self.format)
                self.index = self.index + 1
        worksheet.write('E' + str(self.index - 1), "TP\n")
        self.countpass += 1
        worksheet2.write('A2', self.countpass)
        worksheet2.write('C2', self.countpass + self.countfail)
        worksheet2.write('D2', (self.countpass / (self.countpass + self.countfail))*100)

    def __reconnect(self):
        try:
            self.bot.close()
        except:
            pass
        self.bot = self.__startConnection()
        return self.bot

    def __startConnection(self):
        socket = WebSocketClient(self.__getWSSUrl(), self.botId, self.botName, self.welcomeMessageCount)
        socket.connect()
        return socket

    def __getWSSUrl(self):

        payload = "{\"botInfo\":{\"chatBot\":\"" + self.botName + "\",\"taskBotId\":\"" + self.botId + "\"},\"token\":{}}"
        token = getAuthToken(self.botId, self.botName)
        headers = {
            'authorization': "bearer " + token,
            'origin': HOST,
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-US,en;q=0.8",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            'content-type': "application/json",
            'accept': "application/json",
            'referer': HOST + "bt",
            'connection': "keep-alive",
            'cache-control': "no-cache"
        }
        response = requests.request("POST", RTM_URL, data=payload, headers=headers, verify=VERIFY_SSL_CERT)
        debug.info(response.text)
        messageJson = json.loads(response.text)
        return messageJson["url"]

    def extractMessageText(self, messageObj):
        message = messageObj["cInfo"]["body"]
        if len(message) > 0:
            return message, messageObj["component"]
        else:
            if messageObj["component"]:
                component = messageObj["component"]
                if component["type"] == "text":
                    message = component["payload"]["text"]
                elif component["type"] == "template" and component["payload"] and component["payload"]["payload"]:
                    message = component["payload"]["payload"]["text"]
        return message, messageObj["component"]


def validateContains(actual, expected):
    aWords = re.split("\W", actual)
    eWords = re.split("\W", expected)
    actualWords = ""
    expectedWords = ""
    for word in aWords:
        if word.strip() != '':
            actualWords = actualWords + " " + word

    for word in eWords:
        if word.strip() != '':
            expectedWords = expectedWords + " " + word

    debug.info("Actual Words:" + actualWords)
    debug.info("Expected Words:" + expectedWords)
    return expectedWords in actualWords
