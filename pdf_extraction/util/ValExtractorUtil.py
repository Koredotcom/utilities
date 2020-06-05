from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from pdf_extraction.code_util.log.Logger import Logger
from PIL import Image
from collections import defaultdict
from pdf_extraction import constants
import uuid
import re
import traceback
import fitz
import operator
import functools

logger = Logger()
config_manager = ConfigManager()
storage_manager = StorageManager()
pdf_extraction_config = config_manager.load_config(key='pdf_extraction')


class ExtractorUtil(object):
    """common utilities for imm and cli value sheets"""
    def __init__(self):
        self.table_markdown_prefix = '![table]('
        self.table_markdown_suffix = ')'
        self.cropped_rows = []

    def get_image_replacement_text(self, img_url):
        return self.table_markdown_prefix + img_url + self.table_markdown_suffix

    @staticmethod
    def save_image(img):
        image_name = str(uuid.uuid4()) + '.png'
        img_dest = pdf_extraction_config.get("DOWNLOAD_DIRECTORY") + image_name
        img.save(img_dest, format="PNG")
        return img_dest

    def get_row_image(self, page, row_bbox):
        try:
            im = page.crop(row_bbox)
            self.cropped_rows.append(im)    # used in getting component names for cli
            img = im.to_image(resolution=pdf_extraction_config.get('IMAGE_RESOLUTION', 200))
            return self.save_image(img)
        except Exception:
            logger.error('Error in getting row as image')
            logger.debug(traceback.format_exc())

    @staticmethod
    def get_lot_number(page_text, lot_pattern, fallback_pattern):
        """
        get the lot number present at top of page
        :param page_text: string
        :param lot_pattern: string
        :param fallback_pattern: string
        :return: string
        """
        try:
            if page_text:
                occurrences = re.findall(lot_pattern, page_text)
                if occurrences:
                    return occurrences[0]
                occurrences = re.findall(fallback_pattern, page_text)
                if occurrences:
                    return occurrences[0].strip()
                else:
                    logger.warning('unable to find lot number through regex')
                    return ''
            else:
                logger.warning('page_text empty, returning empty string')
                return ''

        except Exception:
            logger.error(traceback.format_exc())

    @staticmethod
    def get_analyzer_from_page(page_text, analyzer_pattern):
        """
                get analyzer if present at top of page
                :param page_text: string
                :param analyzer_pattern: string
                :return: list
                """
        try:
            if page_text:
                occurrences = re.findall(analyzer_pattern, page_text)
                if occurrences:
                    occurrences = list(set(occurrences))
                    occurrences = list(map(lambda occurrence: occurrence.strip(), occurrences))
                    return occurrences
                else:
                    logger.debug('no analyzer name found through pattern')
                    return []

            else:
                logger.warning('page_text empty, returning empty string')
                return []

        except Exception:
            logger.error(traceback.format_exc())
            return ''

    def stitch_images(self, image_list):
        """
        stitch heading and row as a single image
        :param image_list: list
        :return: img_url - string
        """
        try:
            images = map(Image.open, image_list)
            widths, heights = zip(*(i.size for i in images))
            total_height = sum(heights)
            max_width = max(widths)
            new_im = Image.new('RGB', (max_width, total_height))
            x_offset = 0
            y_offset = 0
            for im in images:
                new_im.paste(im, (0, y_offset))
                x_offset += im.size[0]
                y_offset += im.size[1]
            local_file_path = self.save_image(new_im)
            return local_file_path
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def prepare_table_extraction_object(self, row_images, component_list, analyzer_list):
        result = []
        for row_no in xrange(len(row_images)):
            intermediate_result = dict()
            intermediate_result['answer'] = row_images[row_no]
            intermediate_result['component_acronym'] = component_list[row_no][0]
            intermediate_result['component_name'] = component_list[row_no][1]
            intermediate_result['analyzer'] = analyzer_list[row_no]
            result.append(intermediate_result)

        return result

    @staticmethod
    def get_text_objects(page_dict):
        """returns a list of text dicts from pymupdf dict objects"""
        page_lines = []
        try:
            page_dict = page_dict.get('blocks')
            page_dict = list(filter(lambda x: 'lines' in x.keys(), page_dict))  # filter objects having lines in it
            page_lines.extend([line.get('lines') for line in page_dict])  # get line objects
            page_lines = functools.reduce(operator.iconcat, page_lines, [])  # reduce list of lists to list
            page_spans = list(map(lambda x: x.get('spans'), page_lines))
            page_spans = functools.reduce(operator.iconcat, page_spans, [])
            return page_spans
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def get_test_name(self, pdf_loc):
        pdf = fitz.Document(pdf_loc)
        if pdf.pageCount > 0:
            page = pdf.loadPage(0)
            page_dict = page.getText('dict')
            text_dictionaries = self.get_text_objects(page_dict)
            # for obj in text_dictionaries[: constants.SEARCH_RANGE_FOR_TEST_NAME]:
            for obj in text_dictionaries:
                if 25 <= int(obj.get('size')) <= 33:
                    return obj.get('text')
            logger.info('no test name found')
            return ''

        else:
            logger.warning('pdf have 0 pages, failed to extract test name')
            return ''

    def group_same_components_by_analyzer(self, tables_extraction_object):
        """
        :param tables_extraction_object: dict
        :return: dict
        """
        analyzer_dict = defaultdict(list)
        try:
            for table in tables_extraction_object:
                for component_obj in table:
                    analyzer_dict[component_obj.get('component_acronym') + '%' + '$'.join(component_obj.get('analyzer'))].append(component_obj)

            grouped_components = list(analyzer_dict.values())
            compressed_groups = self.compress_grouped_objects(grouped_components)
            tables_extraction_object = compressed_groups
            return tables_extraction_object

        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def compress_grouped_objects(self, grouped_components):
        """
        :param grouped_components:  list
        :return: list
        """
        result = list()
        try:
            for component in grouped_components:
                image_list = list(map(lambda x: x.get('answer'), component))
                image = self.stitch_images(image_list) if len(image_list) > 1 else image_list[0]
                component_list = [component[0].get('component_acronym'), component[0].get('component_name')]
                analyzer_list = component[0].get('analyzer')
                intermediate_output = self.prepare_component_output(image, component_list, analyzer_list, component[0].get('header_image'))
                result.append(intermediate_output)
            return result

        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def prepare_component_output(self, image, component_list, analyzer_list, header_image):
        """
        :param image: string
        :param component_list: list
        :param analyzer_list: list
        :param header_image: string
        :return: dict
        """
        output = dict()
        try:
            output['answer'] = image
            output['component_acronym'] = component_list[0]
            output['component_name'] = component_list[1]
            output['analyzer'] = analyzer_list
            output['header_image'] = header_image
            return output
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def _get_stitched_images(self, heading_image, row_images):
        """
        :param heading_image: string
        :param row_images: list
        :return: list
        """
        heading_image = [heading_image] * len(row_images)
        stitch_image_input = list(zip(heading_image, row_images))
        stitched_images = list(map(self.stitch_images, stitch_image_input))
        return stitched_images

    def stitch_header_images_with_rows(self, table_extraction_object):
        for obj in table_extraction_object:
            stitched_image = self._get_stitched_images(obj.get('header_image'), [obj.get('answer')])
            image_name = stitched_image[0].split('/')[-1]
            image_url = storage_manager.upload(stitched_image[0], image_name)
            obj['answer'] = self.get_image_replacement_text(image_url)
            obj.pop('header_image', None)
        return table_extraction_object
