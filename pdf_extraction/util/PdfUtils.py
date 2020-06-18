#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from pdf_extraction.util import decorator
from pdf_extraction import constants
from pdf_extraction.util.ToC import get_toc
import os
import sys
import pdfplumber
import traceback
import uuid
import fitz
import re
import copy

reload(sys)
sys.setdefaultencoding('utf8')
config_manager = ConfigManager()
storage_manager = StorageManager()
sys.path.append(str(os.getcwd()))
pdf_extraction_config = config_manager.load_config(key="pdf_extraction")


class Utils(object):
    @decorator.timing
    def __init__(self, pdf_loc, logger, extract_tables=False):
        self.logger = logger
        self.pdf_loc = pdf_loc
        self.extract_tables = extract_tables
        self.pdf_plumber_obj = pdfplumber.open(self.pdf_loc)
        self.pdf_MuPDF_obj = fitz.Document(self.pdf_loc)
        self.is_splittable = True  # todo
        self.page_no_pattern = re.compile('\d\s/\s\d')
        self.reference_num_pattern = re.compile('[a-z0-9_]+v.*\..*0', re.IGNORECASE)
        self.doc_year_month_pattern = re.compile('[0-9]{1,4}-[0-9]{1,2}', re.IGNORECASE)

    def get_table_of_contents(self):
        return get_toc(self.pdf_loc)

    # @decorator.timing
    def extract_page_text(self, page_no):
        """A plumber utility to extract page text"""
        page = self.pdf_plumber_obj.pages[page_no]
        try:
            if self.is_splittable:
                bbox = page.bbox
                new_bbox = (0, 90, bbox[2] / 2, bbox[3] - 65)
                first_column = self.__get_text_by_bbox(page, new_bbox)
                first_column = first_column if first_column else ''
                new_bbox = (bbox[2] / 2, 90, bbox[2], bbox[3] - 65)
                second_column = self.__get_text_by_bbox(page, new_bbox)
                second_column = second_column if second_column else ''
                return [first_column, second_column]
            else:
                bbox = page.bbox
                text = self.__get_text_by_bbox(page, bbox)
                return [text]
        except Exception:
            self.logger.debug(traceback.format_exc())
            raise Exception

    @decorator.timing
    def extract_table(self, page_no):
        # list of table objct
        result = []
        table_objects = self.pdf_plumber_obj.pages[page_no].find_tables()
        for table_no in range(len(table_objects)):
            table_data = self.__get_table_object()
            table_data['id'] = str(uuid.uuid4())
            table_data['table_as_text'] = self.__get_table_text(page_no, table_objects[table_no])
            table_data['table_as_image'] = self.get_table_img(table_objects[table_no].bbox, page_no,
                                                              table_data.get('id'))
            result.append(table_data)
        return result

    @decorator.timing
    def get_table_img(self, table_bbox, page_no, image_id):
        """utility to get complete table as an image"""
        try:
            cropped_page = self.pdf_plumber_obj.pages[page_no].crop(table_bbox)
            image_name = image_id + '.png'
            local_image_location = pdf_extraction_config.get("DOWNLOAD_DIRECTORY") + image_name
            img = cropped_page.to_image(resolution=100)
            img.save(local_image_location, format="PNG")
            img_url = storage_manager.upload(local_image_location, image_name)
            if not img_url:
                self.logger.warning('unable to get image url through s3, returning empty url')
            return img_url
        except Exception:
            self.logger.debug(traceback.format_exc())
            raise Exception

    def __get_table_text(self, page_no, table_obj):
        cropped_page = self.pdf_plumber_obj.pages[page_no].crop(table_obj.bbox)
        return cropped_page.extract_text()

    @staticmethod
    def __get_text_by_bbox(page, bbox):
        return page.crop(bbox).extract_text()

    @staticmethod
    def __get_table_object():
        new_dict = dict()
        new_dict['id'] = None
        new_dict['table_as_text'] = None
        new_dict['table_as_image'] = None
        return new_dict

    def remove_footer_from_page_text(self, page_text):
        """
        removes footer content present in the page text
        :param page_text:
        :return: string
        """
        pat_occurences = re.findall(self.page_no_pattern, page_text)
        if pat_occurences:
            index = page_text.find(pat_occurences[-1])
            if index > -1:
                page_text = page_text.replace(page_text[index:], '')
                return page_text
            else:
                self.logger.warning('failed to fetch index of pattern')
                raise Exception  # todo
        else:
            self.logger.warning('No pattern occurrences found to replace footer')
            return page_text

    # @decorator.timing
    def get_pdf_data_object(self):
        """
        creates an object with text, table and image info of a PDF
        @return: list
        """

        result_obj = list()
        pdf_text_by_page = dict()
        try:
            for page_no in xrange(len(self.pdf_plumber_obj.pages)):
                intermediate_obj = dict()
                intermediate_obj['page_no'] = page_no
                intermediate_obj['page_text'] = self.extract_page_text(page_no)
                # extract tables only if required
                intermediate_obj['tables'] = self.extract_table(page_no) if self.extract_tables else []
                result_obj.append(intermediate_obj)
            for page_no in range(self.pdf_MuPDF_obj.pageCount):
                page_text = self.remove_footer_from_page_text(self.pdf_MuPDF_obj[page_no].getText())
                pdf_text_by_page[page_no] = copy.deepcopy(page_text)

            return [result_obj, pdf_text_by_page]
        except Exception:
            self.logger.debug(traceback.format_exc())
            return [list(), dict()]

    def get_image_with_page_bbox(self, page, rect):
        """mupdf: take page within page using bbox"""
        try:
            pix = page.getPixmap(matrix=fitz.Identity, clip=rect, alpha=False)
            new_id = str(uuid.uuid4())
            image_name = new_id + '.png'
            local_image_location = pdf_extraction_config.get('DOWNLOAD_DIRECTORY') + image_name
            pix.writePNG(local_image_location)
            img_url = storage_manager.upload(local_image_location, image_name)
            return img_url
        except Exception:
            self.logger.error(traceback.format_exc())
            raise Exception

    def extract_order_information_cli(self):
        """
        identify bbox of OInfo string and bbox of next heading
         and trim the content needed and get text of it
        @return:
        """
        answer = ''
        try:
            page = self.pdf_MuPDF_obj.loadPage(0)
            toc = self.get_table_of_contents()
            top_slab_occurrences = page.searchFor(constants.ORDER_INFORMATION)
            if not top_slab_occurrences:
                self.logger.warning('order_information not found in page')
                return ''
            bottom_slab_occurrences = page.searchFor(toc[0][1])
            if bottom_slab_occurrences:
                top_slab = top_slab_occurrences[0]
                first_toc_prefix = page.searchFor(constants.FIRST_TOC_PREFIX)
                if first_toc_prefix:
                    first_toc_prefix.sort(key=lambda rect: rect.y0)
                    bottom_slab = first_toc_prefix[0]
                else:
                    bottom_slab = bottom_slab_occurrences[0]
                rect = fitz.Rect(top_slab.x0, top_slab.y0 + 10, page.rect.x1 - 30, bottom_slab.y1 - 10)
                answer = self.get_image_with_page_bbox(page, rect)
            return answer

        except Exception:
            self.logger.error(traceback.format_exc())
            return answer

    @staticmethod
    def index_of(iterable, search_item):
        try:
            index_value = iterable.index(search_item)
        except ValueError:
            index_value = -1
        return index_value

    @staticmethod
    def get_pack_size_output_obj():
        result = dict()
        result['pack_size'] = ''
        result['ref_no'] = ''
        return result

    def get_pack_size_for_catalogues(self, text):
        result = []
        try:
            for line_index in range(len(text)):
                pack_size = re.search(constants.CLI_FLAG_PATTERN, text[line_index])
                if pack_size:
                    pack_size = pack_size.groupdict().get('pack_size')
                if pack_size and 'tests' in text[line_index] and text[line_index][0].isdigit():
                    pack_output = self.get_pack_size_output_obj()
                    start_index = 0
                    end_index = self.index_of(text[line_index], 'tests')
                    output_text = text[line_index][start_index: end_index + 6]  #size of tests is 5
                    output_text = output_text.split()
                    ref_no_found = False
                    ref_no = ''
                    pack_string = ''
                    for word in output_text:
                        if not ref_no_found and word.isdigit():
                            ref_no += word
                        else:
                            if not ref_no_found:
                                ref_no_found = True
                            pack_string += word + ' '

                    pack_output['pack_size'] = pack_string[:-1]
                    pack_output['ref_no'] = ref_no
                    result.append(pack_output)

            return result
        except Exception:
            self.logger.error(traceback.format_exc())
            return []

    def get_pack_size_cli(self):
        try:
            page = self.pdf_MuPDF_obj.loadPage(0)
            order_info_occurrences = page.searchFor(constants.ORDER_INFORMATION)
            if order_info_occurrences:
                page_text = page.getText().lower()
                toc = self.get_table_of_contents()
                start_index = self.index_of(page_text, constants.ORDER_INFORMATION.lower())

                if start_index != -1:
                    end_index = self.index_of(page_text, toc[0][1].lower())
                    first_toc_prefix = self.index_of(page_text, constants.FIRST_TOC_PREFIX.lower())
                    if first_toc_prefix != -1:
                        end_index = first_toc_prefix
                    page_text = page_text[start_index + 16:end_index].split('\n')
                    pack_size = self.get_pack_size_for_catalogues(page_text)
                    return pack_size

                else:
                    self.logger.warning('start index not found')
                    raise Exception
            else:
                self.logger.warning('order information occurrences not found')
                raise Exception

        except Exception:
            self.logger.error(traceback.format_exc())
            return []

    def extract_reference_number(self):
        ref_no = ''
        bbox = self.pdf_plumber_obj.pages[0].bbox
        page = self.pdf_plumber_obj.pages[0]
        # cropped_page = page.crop((bbox[0], bbox[1], bbox[2], bbox[1]+60))
        # page_text = cropped_page.extract_text()
        page_text = page.extract_text().split('\n')[0]
        pattern_matches = self.reference_num_pattern.findall(page_text)
        if pattern_matches:
            ref_no = pattern_matches[0][1:] if pattern_matches[0][0].isupper() else pattern_matches[0]
        return ref_no

    def extract_doc_year_month(self):
        try:
            year_month = ''
            page = self.pdf_plumber_obj.pages[0]
            page_text = page.extract_text()
            page_text = page.extract_text().split('\n').pop()
            pattern_matches = self.doc_year_month_pattern.findall(page_text)
            if pattern_matches:
                year_month = pattern_matches[0]
            return year_month

        except Exception:
            self.logger.error(traceback.format_exc())
            return ''






if __name__ == "__main__":
    pdf_location = ''
    import logging

    utils = Utils(pdf_location, logging.Logger)
