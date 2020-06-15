#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import copy
import os
import sys
import traceback

sys.path.append(str(os.getcwd()))

from pdf_extraction.Extractor import Extractor
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.config.ConfigManager import ConfigManager

config_manager = ConfigManager()
pdf_extraction_conf = config_manager.load_config(key='pdf_extraction')
logger = Logger()


class Method(Extractor):
    def extract(self):
        """
        :return: extraction_result - ExtractionResult
        """
        print ("path is : ", self.args.get("path"))
        if self.args.get('type') == 'c_ps':
            pack_size = self.method_e.extract_pack_size()
            self.extraction_result.pack_size = pack_size

        if self.args.get('type') == 'c_ms':
            result = self.method_e.extract()
            self.extraction_result.faq = result
            self.validate()
            self.extraction_result.extraction_count = len(self.extraction_result.faq)

        self.extraction_result.title = 'TODO'
        self.extraction_result.ref_no = 'TODO'
        return self.extraction_result

    def validate(self):
        try:
            result = self.remove_ignored_intents(self.extraction_result.faq, pdf_extraction_conf.get('IGNORE_INTENTS'))
            self.extraction_result.faq = copy.deepcopy(result)
            self.extraction_result.faq = self.add_sub_intents_if_present(self.extraction_result.faq,
                                                                         pdf_extraction_conf.get(
                                                                             'INTENTS_WITH_SUBINTENTS'))
        except Exception:
            logger.error(traceback.format_exc())
            return []