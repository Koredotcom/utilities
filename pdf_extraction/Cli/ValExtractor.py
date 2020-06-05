#!/bin/bash
# -*- coding: utf-8 -*-
#

import json
import os
import re
import sys
import traceback

import fitz
import pdfplumber

from pdf_extraction.Extractor import Extractor
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from pdf_extraction.constants import *
from pdf_extraction.util import decorator
from pdf_extraction.util.ValExtractorUtil import ExtractorUtil

sys.path.append(str(os.getcwd()))
config_manager = ConfigManager()
storage_manager = StorageManager()
pdf_extraction_config = config_manager.load_config(key='pdf_extraction')
extractor_util = ExtractorUtil()
logger = Logger()


class Value(Extractor):

    def extract(self):
        self.value_sheet_util = ValueSheetUtil(self.args.get('path'))
        print ("path is : ", self.args.get("path"))
        template = self.value_sheet_util.identify_analyzer_template()
        logger.info('identified value_sheet template as ' + template)

        if template == VAL_TEMPLATE:
            result = self.value_sheet_util.extract()
            return result
        else:
            logger.info('Extraction could not be done due to invalid template')
            return {}

    def validate(self):
        pass


# noinspection SpellCheckingInspection
class ValueSheetUtil(object):

    def __init__(self, pdf_loc):
        self.pdf_loc = pdf_loc
        self.pdf = None
        self.lot_pattern = None
        self.lot_fallback_pattern = None
        self.analyzer_pattern = None
        self.level_pattern = None
        self.deletable_images = list()
        self.header_text = ''
        self.component_cols = []
        self.value_sheet_pattern = re.compile(r'Component\s*Methods', re.IGNORECASE)

    def load_pdf(self):
        self.pdf = pdfplumber.open(self.pdf_loc)
        self.lot_pattern = re.compile(r'LOT\s*\d{6}')
        self.lot_fallback_pattern = re.compile(r'\s+\d{6}\s+')
        # self.analyzer_pattern = re.compile(r'cobas\s*c?\s*\d+/?\d*')
        self.analyzer_pattern = re.compile(r'cobas\s*(?:c?\s*\d{3}/?\d*|integra[\s/\n]400[\s+/\n]plus[\s+/\n]analyzer)',
                                           re.IGNORECASE)
        self.level_pattern = re.compile(r'level\s*\w{1,3}\s*|Positive|Negative', re.IGNORECASE)

    def identify_analyzer_template(self):
        """Identify IC VS template"""
        doc = fitz.Document(self.pdf_loc)
        logger.info('identifying template ...')
        if doc.pageCount >= 1:
            page_number = 0
            page_one_text = doc.getPageText(page_number, output="text")
            occurrences = re.findall(self.value_sheet_pattern, page_one_text)
            if occurrences:
                return VAL_TEMPLATE
            else:
                return INVALID_TEMPLATE
        else:
            logger.info('pdf have 0 pages')
            return INVALID_TEMPLATE

    def add_first_column_bbox(self, page, row_bbox):
        column_bbox = (row_bbox[0] + CC_VS_ROW_DELTA.get('x0'), row_bbox[1], row_bbox[0], row_bbox[3])
        component_column = page.crop(column_bbox)
        self.component_cols.append(component_column)

    def _adjust_bbox_for_row(self, page, row_bbox):
        """
        :rtype: tuple
        :param row_bbox: tuple
        """
        try:
            self.add_first_column_bbox(page, row_bbox)
            row_bbox = list(row_bbox)
            row_bbox[0] += CC_VS_ROW_DELTA.get('x0')
            row_bbox[2] += CC_VS_ROW_DELTA.get('x1')
            return tuple(row_bbox)
        except Exception:
            logger.error(traceback.format_exc())

    def _get_heading_image(self, page, table):
        new_bbox = self._adjust_bbox_for_row(page, table.rows[0].bbox)
        heading = extractor_util.get_row_image(page, new_bbox)
        return heading

    def _get_component_names(self):
        component_list = []
        try:
            # this is populated while cropping rows in util file
            if self.component_cols:
                for row in self.component_cols[1:]:
                    text = row.extract_text()
                    text = text.split('\n')
                    text = list(filter(lambda string: len(string.strip()) > 0, text))
                    component_data = []
                    if len(text) > 0:
                        component_data.append(text[0].strip())
                    if len(text) > 1:
                        component_data.append(text[1].strip())
                    else:
                        component_data.append('') if len(component_list) == 1 else component_list.extend(['', ''])
                    component_list.append(component_data)
            return component_list
        except Exception:
            logger.error(traceback.format_exc())

    def _is_valid_table(self, page, table):
        if self.header_text:
            first_row_bbox = table.rows[0].bbox
            new_page = page.crop(first_row_bbox)
            table_header_text = new_page.extract_text()
            if table_header_text and table_header_text.startswith(self.header_text):
                return True
            return False

    def _convert_table_to_images(self, table, page, header_count=1):
        """
        converts each row in to an image
        :param header_count: int, number of rows to be considered as headings and to be ignored
        :param table: PDFPlumber table object
        :param page: PDFPlumber page object
        :return: list
        """
        try:
            heading_image = self._get_heading_image(page, table)
            row_as_images = [
                extractor_util.get_row_image(page, self._adjust_bbox_for_row(page, table.rows[row_number].bbox))
                for row_number in xrange(header_count, len(table.rows))
            ]
            return [heading_image, row_as_images]
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def get_level_info(self, table, page):
        """
        searches for level information on region above first column of table
        :rtype: str
        :param table: PDF plumber table object
        :param page: PDF plumber page object
        """
        table_bbox = table.bbox
        table_bbox = list(table_bbox)
        table_bbox[0] += CC_VS_ROW_DELTA.get('x0')
        table_bbox[3] = table_bbox[1]
        table_bbox[1] -= 42
        try:
            text = page.crop(tuple(table_bbox)).extract_text()
            if text:
                occurences = re.findall(self.level_pattern, text)
                if len(occurences) == 1:
                    occurence = ' '.join(occurences[0].lower().strip().split())
                    occurence = LEVEL_LOOKUP.get(occurence, '')
                    return occurence
                else:
                    logger.warning('multiple/no levels found, returning empty string')
                    return ''

            else:
                logger.warning('Page_Number- ' + str(page.page_number - 1) + ': No text found in searched region for '
                                                                             'level, returning empty string')
                return ''

        except Exception:
            logger.error(traceback.format_exc())
            return ''

    def extract_for_standard_layout(self, analyzer_template):
        if analyzer_template == STANDARD_LAYOUT:
            result = dict()
            result['tables'] = []
            header_count = 1
            try:
                for page_no in xrange(len(self.pdf.pages) - 1):  # exclude last page
                    page = self.pdf.pages[page_no]
                    table_objects = page.find_tables()  # table object

                    if table_objects:
                        page_text = page.extract_text()
                        page_tables = page.extract_tables()  # table content
                        analyzer = extractor_util.get_analyzer_from_page(page_text, self.analyzer_pattern)
                        result['lot_number'] = extractor_util.get_lot_number(page_text, self.lot_pattern,
                                                                             self.lot_fallback_pattern)
                        for table_no in xrange(len(table_objects)):
                            level = self.get_level_info(table_objects[table_no], page)
                            if not self.header_text:
                                self.header_text = page_tables[table_no][0][0].split()[0]

                            if self.header_text and self._is_valid_table(page, table_objects[table_no]):
                                header_image, row_images = self._convert_table_to_images(table_objects[table_no], page,
                                                                                         header_count)
                                self.deletable_images.append(header_image)
                                self.deletable_images.extend(row_images)
                                component_list = self._get_component_names()
                                self.component_cols = []  # empty it after retrieving component name
                                analyzer_list = [analyzer] * (len(page_tables[table_no]))
                                table_extraction_object = extractor_util.prepare_table_extraction_object(row_images,
                                                                                                         component_list,
                                                                                                         analyzer_list)

                                for table in table_extraction_object:
                                    table['level'] = level
                                    table['header_image'] = header_image

                                result['tables'].append(table_extraction_object)

                # couple components with same analyzer in the table_extraction_object object
                result['tables'] = extractor_util.group_same_components_by_analyzer(result.get('tables'))
                self.deletable_images.extend([obj.get('answer') for obj in result.get('tables')])

                # stitch answer and header image and remove header image key in the table_extraction_object
                result['tables'] = extractor_util.stitch_header_images_with_rows(result.get('tables'))
                return result

            except Exception:
                logger.error(traceback.format_exc())
                raise Exception

    @decorator.timing
    def extract(self):
        """initiates extraction and populates output object"""

        self.load_pdf()
        analyzer_template = STANDARD_LAYOUT
        logger.info('identified analyzer template as - ' + analyzer_template)
        try:
            result = dict()
            if analyzer_template == STANDARD_LAYOUT:
                result = self.extract_for_standard_layout(analyzer_template)

            if result:
                test_name = extractor_util.get_test_name(self.pdf_loc)
                result['test_name'] = test_name

                self.deletable_images = list(set(self.deletable_images))
                storage_manager.delete_local_files(self.deletable_images)
                return result
        except Exception:
            logger.error(traceback.format_exc())
            if self.deletable_images:  # delete intermediate images
                self.deletable_images = list(set(self.deletable_images))
                storage_manager.delete_local_files(self.deletable_images)
            return dict()


if __name__ == '__main__':
    path = '/home/satyaaditya/Downloads/failed/3.pdf'
    val = Value({"type": "e_ms", "path": path})
    result_ = val.extract()
    with open('output.json', 'w') as fp:
        json.dump(result_, fp, indent=4)
