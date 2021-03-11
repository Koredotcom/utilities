from TestSuite import *
import json
import flask
from flask import request

import os
import pandas
from flask_cors import CORS

ALLOWED_EXTENSIONS = {'xlsx'}
app = flask.Flask(__name__)
CORS(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/testcase/upload_and_run', methods=['POST'])
def add_run_testcase():
    try:
        print('===================Testcase execution started ===========================')
        rec = request.json
        debug.info(rec['url'])
        if not allowed_file(rec['url']):
            return flask.jsonify({'error':'Invalid file format'})
        xls = pandas.ExcelFile(rec['url'])
        sheetNames = xls.sheet_names
        sheetNames_lower ={}
        for sheetName in sheetNames:
            sheetNames_lower[sheetName.lower()]= sheetName
        sheetNames = [element.lower() for element in sheetNames];sheetNames
        #print('----',sheetNames)
        #debug.info("sheet names : "+sheetNames)
        if 'prompt' in sheetNames:
            conv_messages = build_prompt_messages(rec, sheetNames_lower)
        if 'non-prompt' in sheetNames:
            build_non_prompt_messages(conv_messages, rec, sheetNames_lower)
        testName = "MS_Multiturn"
        now = datetime.now()
        fileName = 'TestResults/' + testName + str(now.replace(microsecond=0)) + '.xlsx'
        fileName = fileName.replace(':', "-")
        testSuite = TestSuite(testName, conv_messages,fileName)
        countpass, countfail = testSuite.begin()
        print('===================Testcase execution Completed ===========================')
        return flask.jsonify({"Pass": countpass, "Fail": countfail,"Output":os.path.abspath(fileName)}), 200
    except:
        return flask.jsonify({'error': 'Something is wrong!! Please check the test sheet and try again'})


def build_non_prompt_messages(conv_messages, rec, sheetNames_lower):
    excel_data_df = pandas.read_excel(rec['url'], sheet_name=sheetNames_lower['non-prompt'])
    json_str = excel_data_df.to_json(orient='records')
    json_obj = json.loads(json_str)
    for data in json_obj:
        #   print(data)
        messages = []
        message_temp = {
            "input": "",
            "outputs": [
            ]
        }
        if conv_messages.get(data['ConversationId']) is not None:
            messages = conv_messages[data['ConversationId']]
        message_temp['input'] = data['input']
        message_temp['outputs'].append(data['output'])
        message_temp['SequenceId'] = data['SequenceId']
        messages.append(message_temp)
        messages.sort(key=lambda i: i['SequenceId'])
        conv_messages[data['ConversationId']] = messages


def build_prompt_messages(rec, sheetNames_lower):
    excel_data_df = pandas.read_excel(rec['url'], sheet_name=sheetNames_lower['prompt'])
    json_str = excel_data_df.to_json(orient='records')
    json_obj = json.loads(json_str)
    conv_messages = {}
    for data in json_obj:
        #  print(data)
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
        message_temp['outputs'][0]['contains'] = data['output']
        message_temp['SequenceId'] = data['SequenceId']
        messages.append(message_temp)
        messages.sort(key=lambda i: i['SequenceId'])
        conv_messages[data['ConversationId']] = messages
    return conv_messages


app.run()
