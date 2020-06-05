#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys

from pdf_extraction.Extractor import Extractor

sys.path.append(str(os.getcwd()))


class Calib(Extractor):
    def extract(self):
        print('calib extract called')
        self.extraction_result.name = "calib"
        return self.extraction_result

    def validate(self):
        pass


if __name__ == "__main__":
    me = Calib()
    pass
