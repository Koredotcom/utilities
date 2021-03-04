import logging as debug
import os
import json
from auth import *
from getpass import getpass
import argparse
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('--config', help='test config json file', default="test_config.json")
parser.add_argument('--results_html', help='results html file', default="Results.html")
args = parser.parse_args()

testConfig = args.config
resultsHtml = args.results_html


def getToken():
    jwt_data = {
        "clientId": "cs-5dba53b9-a5a3-5ea1-9c33-bbd6f968e6da",
        "clientSecret": "CHa6w7yVXf7AmM9HvuOg5uV6YbCS1ObdX2BtZftDyz8=",
        "identity": str(uuid.uuid4())
    }
    jwt_resp = requests.post('https://philips.kore.ai/api/users/sts', json=jwt_data)
    jwt = jwt_resp.json()['jwt'];
    grant_data = {"assertion": jwt,
                  "botInfo": {"chatBot": "Morgan Stanley POC", "taskBotId": "st-b334e88c-9b70-5012-8298-eecb3af5dc2d"},
                  "token": {}}
    grant_resp = requests.post('https://bots.kore.ai/api/oAuth/token/jwtgrant', json=grant_data)
    access_token = grant_resp.json()['authorization']['accessToken'];
    return access_token

with open(testConfig) as json_data:
    config_json = json.load(json_data)
    token = getToken()
    config_json['AuthToken'] = token

HOST = config_json['HOST']
authToken = config_json.get('AuthToken', None)
username = config_json.get('user_name', None)
password = config_json.get('password', None)
streamTokens = {}
RTM_URL = HOST + "/api/1.1/rtm/start"
REFERER_URL = HOST + "/bt"
LOGFILE = config_json['LOGFILE']
DEBUG = config_json['DEBUG']
VERIFY_SSL_CERT = config_json.get('VERIFY_SSL_CERT', True)
IS_BUILDER = config_json.get('BUILDER', False)

debug.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s ', datefmt='%m/%d/%Y %I:%M:%S %p', filename=LOGFILE,
                  level=debug.DEBUG if DEBUG else debug.INFO)
log = debug.debug


def getAuthToken(botId, botName):
    global authToken, username, password
    if authToken:
        return authToken

    if not username:
        # username = "services1@testadmin2.xyz"
        # password = "Sriram@123"
        username = input("Please enter your email id")
    if not password:
        password = getpass("Please enter your password")

    authToken = getRTMAuthToken(HOST + "/api/1.1", botId, botName, username, password)
    return authToken
