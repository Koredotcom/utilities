from flask import Flask, render_template, send_file, send_from_directory
from flask_cors import CORS
import requests
from dateutil import parser
import json
import os
from os import path

app = Flask(__name__)
CORS(app)


@app.route('/dashboard')
def homepage():
    URL = "http://demo.kore.net/schedulemeeting/post_meeting/info/get"
    data = requests.get(url=URL).json()
    rows = []
    for idx, record in enumerate(data):
        obj = {}
        obj["no"] = idx + 1
        obj["participants"] = [participant['EmailAddress']["Name"] for participant in json.loads(record["to"])]
        end_date = parser.parse(record["endDateTime"])
        start_date = parser.parse(record["startDateTime"])
        obj["from_time"] = start_date.strftime('%Y-%m-%d:%H-%M-%S')
        obj["to_time"] = end_date.strftime('%Y-%m-%d:%H-%M-%S')
        obj["status"] = "Completed"
        obj["owner"] = json.loads(record["from"])['EmailAddress']["Name"]
        obj["record"] = record["recordingUrl"]
        if record["transcript"]:
            obj["transcript"] = json.loads(record["transcript"])[0]["Google"]
        obj["conversation"] = []
        if ("conversation" in record) and (record["conversation"]):
            conversation = json.loads(record["conversation"])
            if conversation and 'Google' in conversation[0] and conversation[0]["Google"]:

                for convers in conversation[0]["Google"]:
                    speaker, text = convers.split(":")
                    obj["conversation"].append((speaker, text))
        rows.append(obj)
    header = ["No", "Owner", "Participants", "From", "To", "Status", "Record", "Transcipt", "Conversation"]
    return render_template("main.html", header=header, rows=rows)


@app.route('/download/<path:url>')
def return_files(url):
    try:
        if "//" not in url:
            splitUrl = url.split(":");
            url = splitUrl[0] + ":/" + splitUrl[1]
        file_path = "static/audio/%s.%s" % (url.split("/")[-1].split(".")[0], "wav")
        if not path.exists(file_path):
            with open(file_path, 'wb') as f:
                r = requests.get(url)
                f.write(r.content)
            f.close()
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(str(e))
        return "File Not Found", 404


if __name__ == "__main__":
    app.run(port=7273)
