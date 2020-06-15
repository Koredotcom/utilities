from pdf_extraction.util import decorator
from pdf_extraction.Extractor import Extractor
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.constants import *
from pdf_extraction.util.ValExtractorUtil import ExtractorUtil
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager

import json
import pdfplumber
import traceback
import fitz
import os
import sys
import re

sys.path.append(str(os.getcwd()))
config_manager = ConfigManager()
storage_manager = StorageManager()
extractor_util = ExtractorUtil()
pdf_extraction_config = config_manager.load_config(key='pdf_extraction')
logger = Logger()


class Value(Extractor):
    def extract(self):
        self.value_sheet_util = ValueSheetUtil(self.args.get('path'))
        print ("path is : ", self.args.get("path"))
        template = self.value_sheet_util.identify_value_sheet_template()
        logger.info('identified value_sheet template as ' + template)

        if template == VAL_TEMPLATE:
            result = self.value_sheet_util.extract()
            logger.info('Imm value sheet extraction completed, extraction_count - {}'.format(
                len(result.get('tables', []))))
            return result
        else:
            logger.warning("Extraction could not be done due to invalid template")
            return {}

    def validate(self):
        pass


class ValueSheetUtil(object):
    def __init__(self, pdf_loc):
        self.pdf_loc = pdf_loc
        self.val_pattern = re.compile(r'Components\s*Method')
        self.amendment_pattern = re.compile(r'Kit\s*Bottle')
        self.pdf = None
        self.lot_pattern = None
        self.lot_fallback_pattern = None
        self.analyzer_pattern = None
        self.deletable_images = None

    @decorator.timing
    def load_pdf(self):
        """ load pdf file in plumer """
        self.pdf = pdfplumber.open(self.pdf_loc)
        self.lot_pattern = re.compile(r'LOT\s*\d{6}')
        self.lot_fallback_pattern = re.compile(r'\s+\d{6}\s+')
        self.analyzer_pattern = re.compile(r'e\s*\d{3}\s+', re.IGNORECASE)
        self.deletable_images = list()

    def identify_value_sheet_template(self):
        """Identify IC VS template"""
        doc = fitz.Document(self.pdf_loc)
        logger.info('\nidentifying template ...')
        if doc.pageCount >= 1:
            page_number = 0
            page_one_text = doc.getPageText(page_number, output="text")
            occurrences = re.findall(self.amendment_pattern, page_one_text)
            if occurrences:
                return AMENDMENT_TEMPLATE
            occurrences = re.findall(self.val_pattern, page_one_text)
            if occurrences:
                return VAL_TEMPLATE
            # print page_one_text
            return INVAL_TEMPLATE
        else:
            return INVAL_TEMPLATE

    @staticmethod
    def _modify_heading_bbox(table):

        """
        modifies bbox to get bbox of headings
        :param table: table object
        :return: tuple - bbox
        """
        try:
            new_bbox = list(table.rows[0].bbox)
            new_bbox[3] += table.rows[1].bbox[3] - table.rows[1].bbox[1]
            return tuple(new_bbox)
        except Exception:
            logger.error(traceback.format_exc())

    def _get_heading_image(self, page, table):
        if table.rows > 1:
            new_bbox = self._modify_heading_bbox(table)
            heading = extractor_util.get_row_image(page, tuple(new_bbox))
            return heading

    def _get_template_type_by_analyzer(self):
        """
        identifies the template type where analyzer is part of table or not
        :return:
        """
        table = None

        for page in self.pdf.pages:
            tables = page.extract_tables()
            if tables:
                table = tables[0]
                break

        if table:
            if len(table) == 2:
                return BETWEEN_TABLE_ANALYZER  # Analyzer is in between tables

            second_row = table[1]
            condition_text = second_row[2]
            if condition_text is None:
                return IN_TABLE_ANALYZER  # analyzer is part of table
            elif True:
                return FIRST_PAGE_ANALYZER  # analyzer is at top of sheet, lot exists
            else:
                return INVALID_TEMPLATE
        else:
            logger.warning('no tables found in the pdf')
            return INVALID_TEMPLATE

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
            row_as_images = [extractor_util.get_row_image(page, table.rows[row_number].bbox)
                             for row_number in xrange(header_count, len(table.rows))]  # first two rows are not required
            return [heading_image, row_as_images]
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def extract_in_out_analyzer_templates(self, analyzer_template):
        """
        If analyzer is outside table, pass analyzer info to all rows, that makes both templates uniform
        Same components are stitched together
        @param analyzer_template: str
        """
        if analyzer_template == FIRST_PAGE_ANALYZER or analyzer_template == IN_TABLE_ANALYZER:
            header_count = 2
            result = dict()
            result['tables'] = []
            analyzer = None

            for page_no in xrange(len(self.pdf.pages)):
                page = self.pdf.pages[page_no]
                table_objects = page.find_tables()  # table object

                if table_objects:
                    page_text = page.extract_text()
                    page_tables = page.extract_tables()  # table content

                    if analyzer_template == FIRST_PAGE_ANALYZER and analyzer is None:
                        analyzer = extractor_util.get_analyzer_from_page(page_text, self.analyzer_pattern)

                    result['lot_number'] = extractor_util.get_lot_number(page_text, self.lot_pattern,
                                                                         self.lot_fallback_pattern)

                    for table_no in xrange(len(table_objects)):
                        header_image, row_images = self._convert_table_to_images(table_objects[table_no], page,
                                                                                 header_count)
                        self.deletable_images.append(header_image)
                        self.deletable_images.extend(row_images)
                        component_list = [[row[0], row[1]] for row in page_tables[table_no]][2:]

                        analyzer_list = [[row[2]] for row in page_tables[table_no]][
                                        2:] if analyzer_template == IN_TABLE_ANALYZER else [analyzer] * (
                                len(page_tables[table_no]) - 2)

                        table_extraction_object = extractor_util.prepare_table_extraction_object(row_images,
                                                                                                 component_list,
                                                                                                 analyzer_list)
                        for obj in table_extraction_object:
                            obj['header_image'] = header_image

                        result['tables'].append(table_extraction_object)

            result['tables'] = extractor_util.group_same_components_by_analyzer(result.get('tables'))

            self.deletable_images.extend([obj.get('answer') for obj in result.get('tables')])

            # stitch answer and header image and remove header image key in the table_extraction_object
            result['tables'] = extractor_util.stitch_header_images_with_rows(result.get('tables'))

            return result

    def _is_header_table(self, page, table):
        """
        :param page: pdf plumber Page object
        :param table: pdf plumber table object
        :return: bool
        """
        try:
            table_bbox = table.bbox
            text = page.crop(table_bbox).extract_text()
            occurrences = re.findall(self.val_pattern, text)
            return True if occurrences else False
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def find_analyzer(self, page, prev_table_obj, cur_table_obj):
        try:
            prev_table_bbox = prev_table_obj.bbox
            cur_table_bbox = cur_table_obj.bbox
            new_bbox = (prev_table_bbox[0], prev_table_bbox[3], cur_table_bbox[2], cur_table_bbox[1] - 1)
            text = page.crop(new_bbox).extract_text()
            analyzer = extractor_util.get_analyzer_from_page(text, self.analyzer_pattern)
            return analyzer

        except Exception:
            logger.warning(traceback.format_exc())
            return ''

    def extract_between_table_analyzer_template(self, analyzer_template):
        """
        extracts from between table analyzer template
        stitch header image to all rows, group same components together
        :param analyzer_template:
        :return:
        """
        result = dict()

        if analyzer_template == BETWEEN_TABLE_ANALYZER:
            result['tables'] = []
            result['lot_number'] = ''
            analyzer = None
            header_image = ''

            for page_no in xrange(len(self.pdf.pages)):
                page = self.pdf.pages[page_no]
                table_objects = page.find_tables()  # return plumber table objects

                if not result.get('lot_number'):
                    page_text = page.extract_text()
                    result['lot_number'] = extractor_util.get_lot_number(page_text, self.lot_pattern,
                                                                         self.lot_fallback_pattern)

                if table_objects:
                    page_tables = page.extract_tables()

                    for table_index in xrange(len(table_objects)):
                        is_header_table = self._is_header_table(page, table_objects[table_index])
                        if is_header_table:  # keep this check to handle even if header updates in pdf
                            header_table = table_objects[table_index]
                            header_image = extractor_util.get_row_image(page, header_table.bbox)
                            self.deletable_images.append(header_image)

                        else:
                            if table_index > 0:
                                analyzer = self.find_analyzer(page, table_objects[table_index - 1],
                                                              table_objects[table_index])

                            row_images = [extractor_util.get_row_image(page, row.bbox) for row in
                                          table_objects[table_index].rows]
                            self.deletable_images.extend(row_images)

                            component_list = [[row[0], row[1]] for row in page_tables[table_index]]
                            analyzer_list = [analyzer] * len(page_tables[table_index])

                            table_extraction_object = extractor_util.prepare_table_extraction_object(row_images,
                                                                                                     component_list,
                                                                                                     analyzer_list)
                            for obj in table_extraction_object:
                                obj['header_image'] = header_image

                            result['tables'].append(table_extraction_object)

            # couple components with same analyzer in the table_extraction_object object
            result['tables'] = extractor_util.group_same_components_by_analyzer(result.get('tables'))

            self.deletable_images.extend([obj.get('answer') for obj in result.get('tables')])

            # stitch answer and header image and remove header image key in the table_extraction_object
            result['tables'] = extractor_util.stitch_header_images_with_rows(result.get('tables'))

        return result

    @decorator.timing
    def extract(self):
        """initiates extraction and populates output object"""

        self.load_pdf()
        analyzer_template = self._get_template_type_by_analyzer()
        logger.info('identified analyzer template as - ' + analyzer_template)

        try:
            result = dict()
            if analyzer_template == IN_TABLE_ANALYZER or analyzer_template == FIRST_PAGE_ANALYZER:
                result = self.extract_in_out_analyzer_templates(analyzer_template)

            elif analyzer_template == BETWEEN_TABLE_ANALYZER:
                result = self.extract_between_table_analyzer_template(analyzer_template)

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
    # todo : convert deletable images to set from list
    # path = '/home/satyaaditya/Documents/test I _ CC sheets/new_template/IC-4.pdf'
    path = '/home/satyaaditya/Downloads/failed/2.pdf'
    val = Value({"type": "e_vs", "path": path})
    output = val.extract()
    with open('output.json', 'w') as fp:
        json.dump(output, fp, indent=4)
