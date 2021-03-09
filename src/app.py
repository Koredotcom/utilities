from TestSuite import *
import json
from html.parser import HTMLParser
from pymongo import MongoClient
import flask
from flask import Flask, flash, request, redirect, url_for
from xlsx2html import xlsx2html
from flask import request
from bson.json_util import dumps
from bson.objectid import ObjectId
import os
import pandas

ALLOWED_EXTENSIONS = {'xlsx'}
app = flask.Flask(__name__)
client = MongoClient('localhost', 27017)


def writeResults(name, countpass, countfail):
    print("SuiteName:", name)
    print("FAILED", countfail)
    print("PASSED", countpass)
    totalConversations = countfail + countpass
    coverage = 100 * (countpass / totalConversations)
    print("TOTAL CASES EXECUTED", (countfail + countpass))
    f = open(resultsHtml, 'a')
    message = """<html>
						<head>
							<style>
								table, th, td {
									border: 1px solid black;
								}
							</style>
						</head>
						<body>
							<br />
							<table width="400">
							<tr>
								<td>Passed conversations</td>
								<td style="color:green; font-weight:bold">""" + str(countpass) + """</td>
							</tr>
							<tr>
								<td>Failed conversations</td>
								<td style="color:red; font-weight:bold">""" + str(countfail) + """</td>
							</tr>
							<tr>
								<td>Total Conversations</td>
								<td style="color:orange; font-weight:bold">""" + str(totalConversations) + """</td>
							</tr>
							<tr>
								<td>Converage</td>
								<td style="color:green; font-weight:bold">""" + str(coverage) + "%""""</td>
							</tr>
							</table>

						</body>
					</html>"""
    # message  = message.format(countpass=str(self.countpass),countfail=str(self.countfail),counttotal=str(self.total))
    # return message
    f.write(message)
    f.close()
    return message


f = open(resultsHtml, 'w')
f.close()


@app.route('/run', methods=['GET'])
def home():
    print('===================Testcase execution started ===========================')
    testName = "MS_Multiturn"
    testSuite = TestSuite(testName)
    countpass, countfail = testSuite.begin()
    message = writeResults(testName, countpass, countfail)
    print('===================Testcase execution Completed ===========================')
    return message


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/testcase/upload_and_run', methods=['POST'])
def add_run_testcase():
    rec = request.json
    print(rec['url'])
    excel_data_df = pandas.read_excel(rec['url'], sheet_name='TestSuite')
    json_str = excel_data_df.to_json(orient='records')
    json_obj = json.loads(json_str)
    conv_messages = {}
    for data in json_obj:
        print(data['ConversationId'])
        messages = []
        message_temp = {
            "input": "",
            "outputs": [
                {
                    "contains": ""
                }
            ]
        }
        if conv_messages.get(data['ConversationId']) is not None:
            messages = conv_messages[data['ConversationId']]
        message_temp['input'] = data['input']
        message_temp['outputs'][0]['contains'] = data['ouput']

        messages.append(message_temp)
        conv_messages[data['ConversationId']] = messages
        print(conv_messages)
    print(messages)
    testName = "MS_Multiturn"
    now = datetime.now()
    fileName = 'TestResults/' + testName + str(now.replace(microsecond=0)) + '.xlsx'
    fileName = fileName.replace(':', "-")
    testSuite = TestSuite(testName, conv_messages,fileName)
    countpass, countfail = testSuite.begin()
    message = writeResults(testName, countpass, countfail)
    print('===================Testcase execution Completed ===========================')
    return flask.jsonify({"Pass": countpass, "Fail": countfail,"Output":os.path.abspath(fileName)}), 200


@app.route('/testResult', methods=['GET'])
def result():
    out_stream = xlsx2html(str(os.path.abspath('./TestResults/MS_Multiturn.xlsx')))
    out_stream.seek(0)
    result_html = out_stream.read()
    return result_html


@app.route('/testcase/add', methods=['POST'])
def add_testcase():
    mydatabase = client['test_cases']
    rec = request.json
    record = mydatabase.myTable.insert_one(rec)
    return flask.jsonify("Succes"), 201


@app.route('/testcase/get/all', methods=['GET'])
def get_testcase():
    mydatabase = client['test_cases']
    cursor = mydatabase.myTable.find()
    list_cur = list(cursor)
    json_data = dumps(list_cur)
    return json_data


@app.route('/testcase/delete/<id>', methods=['DELETE'])
def delete_testcase(id):
    mydatabase = client['test_cases']
    print('id', id);
    result = mydatabase.myTable.delete_one({'_id': ObjectId(id)})
    return result


app.run()
