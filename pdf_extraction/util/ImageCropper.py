import traceback
import uuid
import sys
import os
from wand.image import Image as wand_img
from wand.color import Color
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.code_util.config.ConfigManager import ConfigManager
from pdf_extraction.code_util.storage.StorageManager import StorageManager

sys.path.append(str(os.getcwd()))

logger = Logger()
config_manager = ConfigManager()
storage_manager = StorageManager()

pdf_extraction_config = config_manager.load_config(key='pdf_extraction')


class ImageCropper(object):
    def __init__(self):
        pass

    @staticmethod
    def crop(image_list):
        new_image_list = list()
        try:
            for image_loc in image_list:
                with wand_img(filename=image_loc) as i:
                    i.trim(color=Color('white'))
                    image_name = str(uuid.uuid4()) + '.png'
                    img_dest = pdf_extraction_config.get("DOWNLOAD_DIRECTORY") + image_name
                    i.save(filename=img_dest)
                    new_image_list.append(img_dest)

            return new_image_list
        except Exception:
            logger.error(traceback.format_exc())
            storage_manager.delete_local_files(new_image_list)
            return []


if __name__ == '__main__':
    a = ImageCropper()
    a.crop([])
