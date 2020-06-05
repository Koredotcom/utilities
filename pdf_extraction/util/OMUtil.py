from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager
from pdf_extraction.util.ImageCropper import ImageCropper
from pdf_extraction.code_util.log.Logger import Logger
from copy import deepcopy
from PIL import Image
from collections import Counter
import traceback
import operator
import functools
import uuid
import sys
import fitz

reload(sys)
sys.setdefaultencoding('UTF8')

logger = Logger()
config_manager = ConfigManager()
storage_manager = StorageManager()
pdf_extraction_config = config_manager.load_config(key='pdf_extraction')


class ExtractorUtil(object):
    def __init__(self):
        self.image_conflate = ImageCropper()
        pass

    @staticmethod
    def reduce_text_blocks_in_page_spans(page_spans):
        """
        :param page_spans: list
        :return:
        """
        reduced_page_spans = []

        for text_list in page_spans:
            try:
                result = deepcopy(text_list[0])
                if len(text_list) > 1:
                    result['size'] = max(map(operator.itemgetter('size'), text_list))
                    text = ''.join(map(operator.itemgetter('text'), text_list))
                    result['text'] = text
                reduced_page_spans.append(result)
            except Exception:
                logger.warning(traceback.format_exc())
                logger.warning("couldn't reduce text blocks in page spans, returning same input object")
                return page_spans
        return reduced_page_spans

    def get_headings_from_page(self, page_dict):
        """returns a list of text dicts from pymupdf dict objects"""
        page_lines = []
        try:
            page_dict = page_dict.get('blocks')
            page_dict = list(filter(lambda x: 'lines' in x.keys(), page_dict))  # filter objects having lines in it
            page_lines.extend([line.get('lines') for line in page_dict])  # get line objects
            page_lines = functools.reduce(operator.iconcat, page_lines, [])  # reduce list of lists to list
            page_spans = list(map(lambda x: x.get('spans'), page_lines))
            page_spans = self.reduce_text_blocks_in_page_spans(page_spans)
            page_spans = list(filter(lambda x: x.get('size') >= 18, page_spans))  # font size of headings and
            return page_spans
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    @staticmethod
    def compact_string(heading):
        revised = ''.join([i if ord(i) < 128 and i.isalnum() else '' for i in heading.strip()])
        revised = ''.join(revised.split())
        return revised

    def is_heading_present_in_page(self, headings_from_page, string):
        """
        :param headings_from_page: list
        :param string: str
        :return: bool
        """
        for heading_obj in headings_from_page:
            try:
                heading = heading_obj.get('text')
                if string in heading:
                    return True
                elif self.compact_string(string) in self.compact_string(heading):
                    return True
            except Exception:
                pass
        return False

    def concat_strings_in_list(self, input_list, delimiter='$'):
        input_list = list(map(str, input_list[:3]))
        return delimiter.join(input_list)

    def create_next_parent_or_sibling_map(self, toc, level=4):
        parent_map = dict()
        for content_index in range(len(toc)):
            if toc[content_index][0] >= level:
                parent_index = content_index + 1
                while parent_index < len(toc):
                    if toc[parent_index][0] <= toc[content_index][0]:
                        key = toc[content_index][1]
                        parent_map[key] = toc[parent_index]
                        break
                    parent_index += 1
        return parent_map

    @staticmethod
    def save_image(img):
        image_name = str(uuid.uuid4()) + '.png'
        img_dest = pdf_extraction_config.get("DOWNLOAD_DIRECTORY") + image_name
        img.save(img_dest, format="PNG")
        return img_dest

    @staticmethod
    def get_image_name_from_path(path):
        """
        :param path: str
        :rtype: str
        """
        if path:
            image_name = path.split('/')[-1]
            return image_name
        else:
            return None  # need to raise exception if empty path

    def get_s3_urls(self, image_list):
        s3_url_list = list()
        for image_path in image_list:
            image_name = self.get_image_name_from_path(image_path)
            image_url = storage_manager.upload(image_path, image_name)
            s3_url_list.append(image_url)
        return s3_url_list

    def stitch_images(self, image_list):
        """
        stitch heading and row as a single image
        :param image_list: list
        :return: img_url - string
        """
        try:
            delete_image = False
            conflated_image_list = []
            if len(image_list) == 1:
                conflated_image_list = self.image_conflate.crop(image_list)
                if conflated_image_list:
                    delete_image = True
                conflated_image_list = conflated_image_list if conflated_image_list else image_list
            else:
                if pdf_extraction_config.get('OMF').get('STITCH_IMAGES'):
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
                    conflated_image_list = self.image_conflate.crop([local_file_path])

                    # this need to be deleted if conflated one is present
                    if conflated_image_list:
                        image_list.append(local_file_path)
                        delete_image = True

                    conflated_image_list = conflated_image_list if conflated_image_list else [local_file_path]
                else:
                    conflated_image_list = self.image_conflate.crop(image_list)
                    if conflated_image_list:
                        delete_image = True
                    conflated_image_list = conflated_image_list if conflated_image_list else image_list

            image_urls = self.get_s3_urls(conflated_image_list)

            if delete_image:
                storage_manager.delete_local_files(image_list)
            return image_urls
        except Exception:
            logger.error(traceback.format_exc())
            storage_manager.delete_local_files(image_list)
            raise Exception

    def get_page_as_image(self, page, bbox):
        try:
            pix = page.getPixmap(matrix=fitz.Matrix(2, 2), clip=bbox, alpha=False)
            new_id = str(uuid.uuid4())
            image_loc = pdf_extraction_config.get('DOWNLOAD_DIRECTORY') + new_id + '.png'
            pix.writePNG(image_loc)
            return image_loc
        except Exception:
            logger.error(traceback.format_exc())
            raise Exception

    def get_parent_map(self, toc, proccessing_level=15):
        parent_list = [''] * (proccessing_level + 1)
        parent_map = dict()
        for content in toc:
            try:
                key = content[1]
                parent_map[key] = []
                if content[0] <= proccessing_level:
                    parent_list[content[0]] = content[1]
                    if content[0] > 0:
                        parent_map[key] = parent_list[0: content[0]][::-1]
            except:
                logger.error(traceback.format_exc())

        return parent_map

    def get_duplicate_toc(self, toc):
        toc = [content[1] for content in toc]
        toc_counter = Counter(toc)
        duplicate_toc = [item for item in toc_counter if toc_counter[item] > 1]
        return duplicate_toc
