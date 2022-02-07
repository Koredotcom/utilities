""" Qna flask routs"""

import json
import os
import uuid
from pdf_extraction.code_util.config import Errors as errors
from pdf_extraction.ExtractionGateway import ExtractionGateway
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from flask import request, Response, make_response, redirect, url_for
from werkzeug.utils import secure_filename

extractionGateway = ExtractionGateway()
config_manager = ConfigManager()
pdf_extraction_config = config_manager.load_config("pdf_extraction")
upload_folder = pdf_extraction_config.get("DOWNLOAD_DIRECTORY")
upload_folder = os.getcwd() + upload_folder
storage_manager= StorageManager()

allowed_ext = set(['png', 'jpg', 'jpeg', 'gif', 'pdf'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext

def init(app):
    """define all the routes related to qna in this method"""

    @app.route("/pdf_extraction/extract", methods=['POST'])
    def extract_knowledge():
        """ extract knowledge """

        if 'fileUrl' not in request.json:
            return make_response(json.dumps(errors.file_url_missing), errors.file_url_missing.get('statusCode'))
            
        if 'type' not in request.json:
            return make_response(json.dumps(errors.ext_type_missing), errors.ext_type_missing.get('statusCode'))

        if 'extractionID' not in request.json:
            return make_response(json.dumps(errors.uid_missing), errors.uid_missing.get('statusCode'))
                        
        extraction_response = extractionGateway.extract(request.json)
        return extraction_response

    @app.route('/file/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            # request headers are case insensitive
            if 'file' not in request.files or 'Subfolder' not in request.headers:
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                sub_folder = request.headers['Subfolder']
                filename = secure_filename(file.filename)

                file_location = os.path.join(upload_folder, filename)
                print file_location
                file.save(file_location)
                file_url = storage_manager.upload(file_location, filename, sub_folder)
                response = make_response(json.dumps({'file_url':file_url}), 200)
                response.headers['Content-Type'] = 'application/json'
                return response

    @app.route('/pdf_extraction/upload_extract', methods=['GET', 'POST'])
    def upload_extract_file():
        if request.method == 'POST':
            # check if the post request has the file part

            if 'file' not in request.files:
                return make_response(json.dumps(errors.file_path_missing), errors.file_path_missing.get('statusCode'))
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                return make_response(json.dumps(errors.file_path_empty), errors.file_path_empty.get('statusCode'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print "filename", filename
                file_uuid = uuid.uuid4().hex
                file_location = os.path.join(upload_folder, filename )
                print file_location
                file.save(file_location)
                args = dict()
                args['fileUrl'] = ""
                args['et_id'] = request.headers.get('extractionID')
                args['type'] = request.headers.get('type')
                args['path'] = file_location

                extraction_response = extractionGateway.extract(args)
                return extraction_response

                # response = make_response(json.dumps({'file_url':file_location}), 200)
                # response.headers['Content-Type'] = 'application/json'
                # return response
            return make_response(json.dumps(errors.unsupported_file_format), errors.unsupported_file_format.get('statusCode'))
