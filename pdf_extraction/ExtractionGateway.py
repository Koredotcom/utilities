""" SearchGateway class talks with mongodb"""

import json
from flask import make_response
from pdf_extraction.code_util.StartupCheck import StartupCheck
from pdf_extraction.code_util.log.Logger import Logger
from pdf_extraction.CreateExtractor import CreateExtractor
from pdf_extraction.code_util.storage.StorageManager import StorageManager

storage_manager = StorageManager()
logger = Logger()


class ExtractionGateway(object):
    """ Class to store trained model for a bot"""

    def __init__(self):
        StartupCheck.initialize()

    @staticmethod
    def extract(request_object):
        """ train ontology and tfidf model """

        args = dict()
        print(json.dumps(request_object, indent=2))
        args['fileUrl'] = request_object.get("fileUrl")
        args['et_id'] = request_object.get("extractionID")
        args['type'] = request_object.get("type")
        result = {}

        if "path" in request_object:
            args['path'] = request_object.get("path")
            status_code = True
        else:
            args['path'], status_code = storage_manager.download(args.get('fileUrl'), args.get('et_id'))
        if not status_code:
            status_code = 400
            result["Error"] = "File Download Failed"
            response = make_response(json.dumps(result), status_code)
            response.headers['Content-Type'] = 'application/json'
            return response
        print(json.dumps(args, indent=2))
        logger.info('\n initiating new extraction')
        extractor = CreateExtractor(args)
        extractor_result = extractor.extract()
        final_response = dict()
        final_response['extractionID'] = args.get('et_id')
        if hasattr(extractor_result, 'faq'):
            final_response['extraction'] = {'faq': extractor_result.faq, 'ref_no': extractor_result.ref_no,
                                            'title': extractor_result.title,
                                            'extraction_count': extractor_result.extraction_count,
                                            }
            if args.get('type') == 'c_ps':
                final_response['extraction']['pack_size'] = extractor_result.pack_size
            logger.info('extraction count - {0}'.format(final_response.get('extraction').get('extraction_count')))
        else:
            final_response['extraction'] = extractor_result

        logger.info('extraction completed...' + '\n' * 3)
        response = make_response(json.dumps(final_response), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
