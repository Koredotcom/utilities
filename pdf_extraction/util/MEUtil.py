#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
import os

sys.path.append(str(os.getcwd()))

from collections import OrderedDict
from pdf_extraction.util.PdfUtils import Utils
from pdf_extraction import constants
import copy
import traceback


class MethodExtractor(object):
    def __init__(self, pdf_loc, document_type, logger, extract_tables=False):
        self.document_type = document_type
        self.extract_tables = extract_tables
        self.logger = logger
        self.utils = Utils(pdf_loc, logger, self.extract_tables)
        self.pdf_data = self.pdf_text_by_page = None

    def check_and_replace_table(self, page_text, table_text, table_replacement_text):
        try:
            if table_text is None:
                self.logger.warning('got image instead of table !!!!')
                return page_text
            else:
                for col_index in range(len(page_text)):
                    if table_text in page_text[col_index]:
                        page_text[col_index] = page_text[col_index].replace(table_text, table_replacement_text)
                return page_text
        except Exception:
            self.logger.error(traceback.format_exc())
            return page_text

    def replace_tables_with_links(self):
        try:
            if self.pdf_data is not None:
                for page_data in self.pdf_data:
                    for table in page_data.get('tables', []):
                        table_replacement_text = self.get_table_replacement_text(table.get('table_as_image'),
                                                                                 constants.TABLE)
                        page_data['page_text'] = self.check_and_replace_table(page_data.get('page_text'),
                                                                              table.get('table_as_text'),
                                                                              table_replacement_text)
            else:
                self.logger.error('Failed loading pdf data from pdfUtils')
                raise Exception

        except Exception:
            self.logger.debug(traceback.format_exc())
            raise Exception

    @staticmethod
    def get_table_replacement_text(img_url, flag=constants.TABLE):
        if flag is constants.TABLE:
            return constants.TABLE_MARK_DOWN_PREFIX + img_url + constants.MARK_DOWN_SUFFIX

    def get_page_text_as_lines_plumber(self):
        lines = list()
        try:
            for page_data in self.pdf_data:
                split_lines = (list(map(lambda x: x.split('\n'), page_data.get('page_text'))))
                for page_lines in split_lines:
                    lines.extend(page_lines)

            return lines
        except Exception:
            self.logger.debug(traceback.format_exc())
            raise Exception

    def get_page_text_lines_mupdf(self):
        lines = list()
        try:
            for page_no in self.pdf_text_by_page:
                split_lines = self.pdf_text_by_page.get(page_no).split('\n')
                lines.extend(split_lines)
            return lines
        except Exception:
            self.logger.debug(traceback.format_exc())
            raise Exception

    def get_qna_pair(self, topic_headings, page_lines):
        updated_page_lines = self.extract_text(topic_headings, page_lines)
        result = self.create_qna_pair(topic_headings, updated_page_lines)
        return result

    @staticmethod
    def substitute_line_sep(qna_pair):
        for pair in qna_pair:
            pair['answer'] = copy.deepcopy(pair['answer'].replace('\n', os.linesep))
        return qna_pair

    def extract_order_information(self, result):
        """
        Order information is present in first row of un-structured table at start of c_ms docs
        @param result: list- qna object
        """

        order_information = ''
        try:
            if self.document_type == 'c_ms':
                order_information = self.utils.extract_order_information_cli()
                order_information = self.get_table_replacement_text(
                    order_information) if order_information else order_information

            elif self.document_type == 'e_ms':
                pass

            result.append({"question": 'Order Information', 'answer': order_information})
            return result
        except Exception:
            self.logger.error(traceback.format_exc())
            return result

    def extract_pack_size(self):
        try:
            if self.document_type in ['c_ps']:
                pack_size = self.utils.get_pack_size_cli()
                return pack_size

            elif self.document_type == ['e_ms', 'e_ps']:
                pass
        except Exception:
            self.logger.error(traceback.format_exc())
            return []

    def extract_reference_number(self):
        return self.utils.extract_reference_number()

    # @decorator.timing
    def extract(self):
        """
        :return: result- list
        """
        try:
            self.pdf_data, self.pdf_text_by_page = self.utils.get_pdf_data_object()
            if self.extract_tables:
                self.replace_tables_with_links()
            page_lines_plumber = self.get_page_text_as_lines_plumber()
            page_lines_mupdf = self.get_page_text_lines_mupdf()
            topic_headings = self.extract_headings()
            qna_pair_plumber = self.get_qna_pair(topic_headings, page_lines_plumber)
            qna_pair_mupdf = self.get_qna_pair(topic_headings, page_lines_mupdf)
            qna_pair_mupdf = self.substitute_line_sep(qna_pair_mupdf)
            result = self.replace_table_answers(qna_pair_plumber, qna_pair_mupdf)
            result = self.extract_order_information(result)
            return result
        except Exception:
            return []

    def replace_table_answers(self, qna_pair_plumber, qna_pair_Mupdf):
        try:
            for pair_index in range(len(qna_pair_plumber)):
                if constants.TABLE_MARK_DOWN_PREFIX in qna_pair_plumber[pair_index].get('answer'):
                    qna_pair_Mupdf[pair_index]['answer'] = copy.deepcopy(qna_pair_plumber[pair_index].get('answer'))
            return qna_pair_Mupdf
        except Exception:
            self.logger.error(traceback.format_exc())
            return []

    def extract_headings(self):
        """Extarct pdf into qna list"""
        toc = self.utils.get_table_of_contents()
        return toc

    def extract_text(self, topic_headings, plain_text):
        """
        Separate topic headings from paragraph content
        :param topic_headings: list
        :param plain_text: list
        :return: list
        """
        topic_index = 0
        plain_text_index = 0
        updated_plain_text = list()
        try:
            while topic_index < len(topic_headings) and plain_text_index < len(plain_text):
                current_heading = topic_headings[topic_index].decode('utf-8')
                compact_current_heading = self.compact_string(topic_headings[topic_index])
                current_plain_text = plain_text[plain_text_index].strip()

                if current_heading == current_plain_text:
                    updated_plain_text.append(current_plain_text)
                    topic_index += 1
                    plain_text_index += 1

                elif current_plain_text.startswith(current_heading):
                    updated_plain_text.append(current_heading)
                    updated_plain_text.append(current_plain_text[len(current_heading):])
                    topic_index += 1
                    plain_text_index += 1

                elif self.compact_string(current_plain_text.strip()).startswith(compact_current_heading):
                    updated_plain_text.append(current_heading)
                    updated_plain_text.append(current_plain_text[len(current_heading):])
                    topic_index += 1
                    plain_text_index += 1

                else:
                    updated_plain_text.append(current_plain_text)
                    plain_text_index += 1

            while plain_text_index < len(plain_text):
                current_plain_text = plain_text[plain_text_index].strip()
                updated_plain_text.append(current_plain_text)
                plain_text_index += 1
            return updated_plain_text
        except Exception:
            self.logger.error(traceback.format_exc())

    @staticmethod
    def compact_string(heading):
        revised = ''.join([i if ord(i) < 128 and i.isalnum() else '' for i in heading.strip()])
        revised = ''.join(revised.split())
        return revised

    def create_qna_pair(self, topic_headings, plain_text_lines):
        """
        Create question asnwer pairs from headings and plain_text, with a max limit of 75 lines for an answer
        @param topic_headings: list of headings in pdf
        @param plain_text_lines: list of text lines with headings in new lines
        @return:
        """

        asnwer_lines = 75

        plain_text_file_length = len(plain_text_lines)
        compact_topic_heading = list(map(self.compact_string, topic_headings))
        line_number = 0
        topic_list = []
        topic_dict = OrderedDict()
        for line in plain_text_lines:
            # print type(line), type(topic_headings[0])
            compact_line = self.compact_string(line)
            if line in topic_headings:
                topic_dict[line.strip()] = {"question": line.strip(), "Line Start": line_number}
            elif compact_line in compact_topic_heading:
                topic_headings_index = compact_topic_heading.index(compact_line)
                topic_dict[topic_headings[topic_headings_index]] = {"question": line.strip(), "Line Start": line_number}

            line_number += 1
        for key, val in topic_dict.items():
            topic_list.append(val)

        if topic_list:
            topic_list.sort(key=lambda heading: heading['Line Start'])

        result_list = []
        for index in range(0, len(topic_list)):

            obj = topic_list[index]
            line_start = obj.get("Line Start")

            answer_range = line_start + asnwer_lines
            next_topic_line_start = sys.maxsize
            if index + 1 < len(topic_list):
                next_topic_line_start = topic_list[index + 1].get("Line Start")

            line_end = min(answer_range, next_topic_line_start, plain_text_file_length)
            updated_obj = copy.deepcopy(obj)
            updated_obj["Line End"] = line_end

            answer = ""
            for linenumer in range(line_start + 1, line_end):
                answer += plain_text_lines[linenumer].strip() + os.linesep
            updated_obj["answer"] = answer
            # print updated_obj
            updated_obj.pop('Line End', None)
            updated_obj.pop('Line Start', None)
            result_list.append(copy.deepcopy(updated_obj))
        return result_list


if __name__ == "__main__":
    me = MethodExtractor('/home/surendra/Documents/pdf_extraction/SHBG.pdf')
    print me.extract()
