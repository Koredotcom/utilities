#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from abc import abstractmethod
import abc
from pdf_extraction.ExtractionResult import ExtractionResult
from pdf_extraction.util.MEUtil import MethodExtractor
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
import os
import sys
import traceback

sys.path.append(str(os.getcwd()))
logger = Logger()
config_manager = ConfigManager()
pdf_extraction_conf = config_manager.load_config(key='pdf_extraction')


class Extractor(object):
    """
    Abstract class
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, args):
        self.args = args
        self.extraction_result = ExtractionResult()
        extract_tables = pdf_extraction_conf.get('EXTRACT_TABLES', False)
        self.method_e = MethodExtractor(self.args.get("path"), self.args.get('type'), logger, extract_tables)

    @abstractmethod
    def extract(self):
        """extracts all headings and its data from a given pdf"""
        print('extract called')
        print(self.extraction_result)
        pass

    @abstractmethod
    def validate(self):
        print('validate called')
        pass


    @staticmethod
    def remove_ignored_intents(faqs, intent_list):
        """
        removes intents which are in ignorable list in config from the extracted faqs
        :param faqs: list
        :param intent_list: list
        :return: list
        """
        faqs = list(filter(lambda x: x.get('question', '') not in intent_list, faqs))
        return faqs

    def add_sub_intents_if_present(self, faqs, sub_intent_dict):
        try:
            intents = list()
            result_list = list()
            for qna in faqs:
                if qna.get('question') in sub_intent_dict:
                    result_list.extend(
                            self.method_e.create_qna_pair(sub_intent_dict.get(qna.get('question')), qna.get('answer').split('\n')))
                else:
                    intents.append(qna)
            if result_list:
                intents.extend(result_list)
            return intents
        except Exception:
            logger.error(traceback.format_exc())
            return []
