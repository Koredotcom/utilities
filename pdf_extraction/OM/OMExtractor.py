#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import copy
import os
import sys
import traceback
import uuid

import fitz

from pdf_extraction import constants
from pdf_extraction.ExtractionResult import ExtractionResult
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from pdf_extraction.util.OMUtil import ExtractorUtil
from pdf_extraction.util.decorator import timing

sys.path.append(str(os.getcwd()))

storage_manager = StorageManager()

config_manager = ConfigManager()
logger = Logger()
pdf_extraction_config = config_manager.load_config(key='pdf_extraction')


class Stack:

    def __init__(self):
        self.stack = []

    def pop(self):
        if len(self.stack) < 1:
            return None
        return self.stack.pop()

    def push(self, item):
        self.stack.append(item)

    def size(self):
        return len(self.stack)

    def top(self):
        return self.stack[-1]


class OM(object):
    def __init__(self, args):
        self.args = args
        self.extraction_result = ExtractionResult()

    def extract(self):
        print ("path is : ", self.args.get("path"))
        om_extractor = OMExtractor(self.args.get('path'))
        result = om_extractor.extract()
        self.extraction_result.faq = result
        self.extraction_result.extraction_count = len(self.extraction_result.faq)
        self.extraction_result.title = 'TODO'
        self.extraction_result.ref_no = 'TODO'
        return self.extraction_result

    def validate(self):
        pass


class OMExtractor(object):
    def __init__(self, pdf_loc):
        self.om_util = ExtractorUtil()
        self.pdf = fitz.Document(pdf_loc)
        self.heading_map = dict()

    @staticmethod
    def get_unique_heading(heading):
        return heading + '$' + str(uuid.uuid4())

    def get_immediate_children_map(self, toc, toc_duplicates):
        stack = Stack()
        children_map = dict()

        for content in toc:
            if stack.size() == 0 or stack.top()[0] <= content[0]:
                stack.push(content)
            else:

                process_level = stack.top()[0] - 1
                while process_level - content[0] >= 0:
                    children = list()
                    while stack.size() and stack.top()[0] > process_level:
                        children.append(stack.pop())

                    if children:
                        heading_key = stack.top()[1]
                        key = self.get_unique_heading(heading_key) if heading_key in toc_duplicates else heading_key
                        children_map[key] = copy.deepcopy(children[::-1])

                    process_level = stack.top()[0] - 1

                stack.push(content)

        if stack.size() > 0:
            while stack.size():
                current_level = stack.pop()
                children = list()
                children.append(current_level)
                while stack.size() and current_level[0] == stack.top()[0]:
                    children.append(stack.pop())

                if stack.size():
                    heading_key = stack.top()[1]
                else:
                    heading_key = 'root'
                key = self.get_unique_heading(heading_key) if heading_key in toc_duplicates else heading_key
                children_map[key] = copy.deepcopy(children[::-1])

        return children_map

    def get_table_of_contents(self):
        simple = self.pdf.getToC(simple=True)
        complex = self.pdf.getToC(simple=False)
        for i in range(len(complex)):
            simple[i] += [{'x': complex[i][3]['to'].x, 'y': complex[i][3]['to'].y}]
        return simple

    @staticmethod
    def modify_page_bbox(page_rect, bbox_delta):
        page_rect.x0 += bbox_delta.get('x0')
        page_rect.y0 += bbox_delta.get('y0')
        page_rect.x1 += bbox_delta.get('x1')
        page_rect.y1 += bbox_delta.get('y1')
        return page_rect

    @staticmethod
    def get_bbox_for_page_border_trim(page, current_bbox):
        try:
            word_occurrences = page.searchFor(pdf_extraction_config.get("SEARCH_STRING"))
            if word_occurrences:
                word_occurrences.sort(key=lambda occurrence: occurrence.y1)
                footer_to_border_delta = word_occurrences[-1].y1 - page.rect.y1
                if footer_to_border_delta >= -65:
                    current_bbox['y1'] = footer_to_border_delta - 10
                    return current_bbox
            return None

        except Exception:
            logger.error(traceback.format_exc())
            return None

    def crop_complete_page(self, page):
        page_trim_bbox = self.get_bbox_for_page_border_trim(page, constants.OM_COMPLETE_PAGE_DELTA)
        page_trim_bbox = page_trim_bbox if page_trim_bbox else constants.OM_COMPLETE_PAGE_DELTA
        page_rect = self.modify_page_bbox(page.rect, page_trim_bbox)
        return self.om_util.get_page_as_image(page, page_rect)

    def extract_by_level(self, simple_toc, level, parent_map):
        result = dict()
        for index in xrange(len(simple_toc)):
            try:
                if simple_toc[index][0] >= level:
                    qna = dict()
                    current_heading_unique = simple_toc[index][1]
                    current_heading = current_heading_unique.split('$')[0]
                    qna['question'] = current_heading
                    if current_heading_unique in self.parent_children_map:
                        qna['children'] = [i[1] for i in self.parent_children_map[current_heading_unique]]
                    else:
                        qna['children'] = list()
                    page_no = simple_toc[index][2] - 1
                    answer_page_count = simple_toc[index + 1][2] - simple_toc[index][2]
                    next_heading_info = copy.deepcopy(simple_toc[index + 1] if index + 1 < len(simple_toc) else [])
                    if next_heading_info:
                        next_heading_info[2] -= 1

                    current_heading_info = copy.deepcopy(simple_toc[index])
                    current_heading_info[2] -= 1
                    answer_page_count = answer_page_count if answer_page_count else 1
                    answer = list()
                    while answer_page_count and page_no < simple_toc[-1][2]:
                        page = self.pdf.loadPage(page_no)
                        if next_heading_info:

                            # both headings in same page
                            if current_heading_info[2] == next_heading_info[2]:
                                heading1_point = current_heading_info[3]
                                heading2_point = next_heading_info[3]
                                crop_bbox = fitz.Rect(heading1_point['x'], page.rect[3] - heading1_point['y'],
                                                      page.rect[2], page.rect[3] - heading2_point['y'])
                                answer.append(self.om_util.get_page_as_image(page, crop_bbox))
                                break

                            # pages in between current and next heading
                            elif answer_page_count and current_heading_info[2] < page_no < next_heading_info[2]:
                                page_url = self.crop_complete_page(page)
                                answer.append(page_url)
                                answer_page_count -= 1

                            # page where next heading is present
                            elif answer_page_count and page_no == next_heading_info[2]:
                                next_heading_point = next_heading_info[3]
                                crop_bbox = fitz.Rect(page.rect[0], page.rect[1],
                                                      page.rect[2] - next_heading_point['x'],
                                                      page.rect[3] - next_heading_point['y'])
                                if crop_bbox.y1 >= 90.0:
                                    answer.append(self.om_util.get_page_as_image(page, crop_bbox))
                                break

                            # start of current heading in the page
                            elif answer_page_count and current_heading_info[2] == page_no:
                                heading1_point = current_heading_info[3]
                                crop_bbox = fitz.Rect(heading1_point['x'], page.rect[3] - heading1_point['y'],
                                                      page.rect[2], page.rect[3])
                                answer.append(self.om_util.get_page_as_image(page, crop_bbox))
                                answer_page_count -= 1

                        else:
                            page_url = self.crop_complete_page(page)
                            answer.append(page_url)
                            answer_page_count -= 1

                        page_no += 1

                    qna['answer'] = self.om_util.stitch_images(answer)
                    qna['parents'] = parent_map.get(current_heading_unique, [])
                    result[current_heading_unique] = copy.deepcopy(qna)
            except Exception:
                logger.error(traceback.format_exc())
                raise Exception

        return result

    @staticmethod
    def identify_level(toc):
        """
        :param toc: list
        :return:    int
        """
        root_node_count = 0
        for entry in toc:
            if entry[0] == 1:  # root node has level 1
                root_node_count += 1
        if root_node_count > 1:
            return 3
        if root_node_count == 1:
            return 4
        else:
            return 3

    def convert_toc(self, toc, duplicates):
        for i in toc:
            if i[1] in duplicates:
                i[1] = self.get_unique_heading(i[1])
        return toc

    @timing
    def extract(self):
        try:
            logger.info('extraction through om initiated ...')
            toc_simple = self.get_table_of_contents()

            duplicate_toc = self.om_util.get_duplicate_toc(toc_simple)
            toc_simple = self.convert_toc(toc_simple, duplicate_toc)

            self.parent_children_map = self.get_immediate_children_map(toc_simple, duplicate_toc)
            with open('toc.json', 'w') as fp:
                json.dump(self.parent_children_map, fp, indent=4)

            level = self.identify_level(toc_simple)
            parent_map = self.om_util.get_parent_map(toc_simple)
            logger.info('processing level - ' + str(level))
            qna_result = self.extract_by_level(toc_simple, level, parent_map)
            logger.info('extracted questions in level {} - {}'.format(level, len(qna_result)))

            logger.info('extraction through om completed ...')
            return qna_result
        except Exception:
            logger.error(traceback.format_exc())
            # return []
            raise Exception


import simplejson as json

if __name__ == "__main__":
    # b = ['c6k', 'c8k', 'c111', 'c311', 'c513', 'e411', 'integra400']
    b = ['c6k']
    for i in b:
        path = '/home/satyaaditya/Documents/Operator manual/om_' + i + '.pdf'
        path = '/home/satyaaditya/Desktop/cobas6k' + '.pdf'
        a = OMExtractor(path)

        result = a.extract()
        with open('output.json', 'w') as fp:
            json.dump(result, fp, indent=4)
