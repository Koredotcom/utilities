#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import sys

from pdf_extraction.Extractor import Extractor

sys.path.append(str(os.getcwd()))


class Control(Extractor):
    def extract(self):
        self.extraction_result.name = "control"
        return self.extraction_result
        pass

    def validate(self):
        pass


if __name__ == "__main__":
    me = Control()
    pass
