#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import sys

sys.path.append(str(os.getcwd()))

from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.config.ConfigManager import ConfigManager

logger = Logger()
config_manager = ConfigManager()
storage_conf = config_manager.load_config(key='pdf_extraction')


class StartupCheck(object):
    """
    StartupCheck 
    """

    @staticmethod
    def create_download_directory(directory_path):
        """
        create_download_directory if not exist
        """
        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                logger.info('Download Directory: Created {0}'.format(directory_path))
            else:
                logger.info('Download Directory: Already exist{0}'.format(directory_path))
            return True
        except:
            logger.error('Error!! in creating download directory {0}'.format(directory_path))
            return False

    @classmethod
    def initialize(cls):
        """
        perform startup_check
        """
        try:
            logger.info('Started..... startup checklist')
            return StartupCheck.create_download_directory(storage_conf.get("DOWNLOAD_DIRECTORY"))
        finally:
            logger.info('Finished.... startup checklist')


if __name__ == '__main__':
    StartupCheck.initialize()
