#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo import ReturnDocument
import os
import sys

sys.path.append(str(os.getcwd()))

import requests
import traceback
import pymongo
import boto3
import glob

from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.config.ConfigManager import ConfigManager

config_manager = ConfigManager()
pdf_extraction_conf = config_manager.load_config(key='pdf_extraction')
db_conf = config_manager.load_config(key='db')
proxy_conf = config_manager.load_config(key='proxy')

logger = Logger()


class Singleton(object):
    """
    Singleton interface:
    http://www.python.org/download/releases/2.2.3/descrintro/#__new__
    """

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass


class StorageManager(Singleton):
    """
    Logger Manager.
    Handles all logging files.
    """

    def init(self):
        self.download_directory = pdf_extraction_conf.get("DOWNLOAD_DIRECTORY")

    def download(self, file_url, uid):
        """
        download the link from web"
        """

        try:
            local_file_path = os.path.join(os.path.abspath(self.download_directory), uid)

            if not proxy_conf.get("USE_PROXY", False):
                r = requests.get(file_url, stream=True, timeout=pdf_extraction_conf.get("DOWNLOAD_TIMEOUT", 10))
            else:
                logger.info('Using proxy configuration')
                r = requests.get(file_url, stream=True, proxies=proxy_conf.get("PROXY_SETTING"),
                                 timeout=pdf_extraction_conf.get("DOWNLOAD_TIMEOUT", 10))

            with open(local_file_path, "wb") as local_file:
                for chunk in r.iter_content(chunk_size=1024):
                    # writing one chunk at a time to file
                    if chunk:
                        local_file.write(chunk)

            # local_file.close()
            r.close()

            logger.debug('Successfully downloaded {0}'.format(file_url))

            return local_file_path, True
        except Exception:
            logger.error('Error!! Download failed {0}'.format(file_url))
            logger.debug(traceback.format_exc())
            return "", False

    def upload(self, local_file_path, file_name, sub_folder=None):
        is_s3_upload = pdf_extraction_conf.get('UPLOAD_TO_S3', False)
        if is_s3_upload:
            s3 = boto3.client('s3')
            sub_folder = pdf_extraction_conf.get("SUB_FOLDER") if sub_folder is None else sub_folder
            try:
                s3.upload_file(local_file_path, pdf_extraction_conf.get("S3_BUCKET_NAME"),
                               '{}/{}'.format(sub_folder, file_name),
                               ExtraArgs={'ContentType': 'image/png'})

                file_url = pdf_extraction_conf.get("IMAGE_HOST_ENDPOINT") + sub_folder + '/' + file_name
                return file_url
            except Exception:
                logger.error("Failed to uplaod image on amazon s3!")
                logger.debug(traceback.format_exc())
                return ''
        else:
            return local_file_path

    @staticmethod
    def delete_local_files(files):
        try:
            for file_path in files:
                os.remove(file_path)
        except Exception:
            logger.error(traceback.format_exc())

class DBManager(Singleton):
    """
    Handles DB operations
    """

    def init(self):
        client = MongoClient(db_conf.get('MONGO_URI'))

        database = client[db_conf.get('DB_NAME')]
        self.extraction_queue = database[db_conf.get('COLLECTION_EXTRACTION_QUEUE')]

    def put_extraction_task(self, request_object):
        """
        insert a job in a qna extraction queue
        """
        extractionTaskId = request_object.get("extractionTaskId", "ke-123")
        logger.info('Inserting extraction task in a queue {0}'.format(extractionTaskId))

        try:
            data = {
                'startTime': None,
                'endTime': None,
                'createdOn': datetime.now(),
                'priority': 1,
                'extractionTaskId': extractionTaskId,
                'payload': request_object
            }
            self.extraction_queue.insert(data)
            return True
        except Exception:
            logger.info('Failed inserting extraction task in a queue {0}'.format(extractionTaskId))
            logger.debug(traceback.format_exc())
            return False

    def get_extraction_task(self):
        """
        fetch a job from a qna extraction queue
        """

        try:
            request_object = self.extraction_queue.find_one_and_update(
                {"startTime": None},
                {"$set": {"startTime": datetime.now()}},
                sort=[('createdOn', pymongo.ASCENDING), ('priority', pymongo.DESCENDING)],
                return_document=ReturnDocument.AFTER
            )
            if request_object:
                logger.info('Fetching an extraction task from a queue {0}'.format(request_object.get("_id")))
                logger.info(request_object.get("extractionTaskId"))
            return request_object
        except Exception:
            logger.info('Failed fetching an extraction task from a queue')
            logger.debug(traceback.format_exc())
            return None

    def end_extraction_task(self, request_object):
        """
        mark job done from a qna extraction queue
        """
        logger.info('Fetching an extraction task from a queue')

        try:
            return self.extraction_queue.update(
                {"_id": ObjectId(request_object.get("_id"))},
                {"$set": {"endTime": datetime.now()}}
            )

        except Exception:
            logger.info('Failed fetching an extraction task from a queue')
            logger.debug(traceback.format_exc())
            return False


if __name__ == '__main__':
    storage_manager = StorageManager()
    db_manager = DBManager()
    print storage_manager.download("http://127.0.0.1:8000/SHBG.pdf", "u-123")
    # print storage_manager.download("https://info.undp.org/erecruit/documents/FAQ.pdf","u-124")
#    request_payload = {
#      "name": "web extraction", 
#      "language": "en", 
#      "extractionTaskId": "ke-bdaf46f4-4fe8-53cd-ab1f-f5dad19955cd", 
#      "fileUrl": "https://seller.flipkart.com/slp/faqs", 
#      "_id": "ke-bdaf46f4-4fe8-53cd-ab1f-f5dad19955cd", 
#      "extractionType": "faq"
#    }
##    print db_manager.put_extraction_task(request_payload)
#    request_object = db_manager.get_extraction_task()
#    print(request_object)
#    if request_object:
#        db_manager.end_extraction_task(request_object)
