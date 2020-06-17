import os
import sys
import json

sys.path.append(str(os.getcwd()))
from pdf_extraction.Imm import MeExtractor
from pdf_extraction.Imm import ValExtractor
from pdf_extraction.Cli import MeExtractor as cli_Me_Extractor
from pdf_extraction.Cli import ValExtractor as cli_Val_Extractor
from pdf_extraction.OM import OMExtractor

class CreateExtractor(object):
    """
     Create an return an appropriate extarctor
    """

    def __init__(self, args):
        self.args = args

    def get_extractor(self):
        """Factory method for extractors"""
        if self.args.get('type') == 'e_ms':
            return MeExtractor.Method(self.args)

        elif self.args.get('type') == 'e_vs':
            return ValExtractor.Value(self.args)

        elif self.args.get('type') == 'c_ms':
            return cli_Me_Extractor.Method(self.args)

        elif self.args.get('type') == 'c_vs':
            return cli_Val_Extractor.Value(self.args)

        elif self.args.get('type') == 'e_ps':
            return MeExtractor.Method(self.args)

        elif self.args.get('type') == 'c_ps':
            return cli_Me_Extractor.Method(self.args)

        # elif self.pdf_type == "calibrator":
        #     return Calibrator.Calibrator(req_obj)

        elif self.args.get('type') == 'om':
            print 'OM called'
            return OMExtractor.OM(self.args)

    def extract(self):
        """
        process req obj
        :return: final_result - dict
        """

        extractor_object = self.get_extractor()
        result = extractor_object.extract()
        return result


if __name__ == "__main__":
    import time

    t1 = time.time()
    for i in range(1,13):
        a = CreateExtractor({"type": "c_ms", "path": "/home/satyaaditya/Downloads/" +str(i)+".pdf"})
        # a = CreateExtractor({"type": "e_vs", "path": "/home/satyaaditya/Documents/RocheSamples/clinical/control/" +str(i)+".pdf"})

        result_ = a.extract()

        with open('output1.json', 'w') as fp:
            json.dump(result_.faq, fp, indent=2)
    print (time.time() - t1) * 1000
    # b = a.get_extractor({"type":"e_ms"})
    # c = b.extract()
    # print(c.name)
