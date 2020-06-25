#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


import os
import sys

sys.path.append(str(os.getcwd()))


class ExtractionResult(object):
    def __init__(self):
        self.title = ''
        self.extraction_count = 0
        self.faq = list()
        self.ref_no = ''
        self.pack_size = []
        self.assay_title =''
        self.assay_acronym = ''

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if isinstance(value, str):
            self.__title = value

    @property
    def extraction_count(self):
        return self.__extraction_count

    @extraction_count.setter
    def extraction_count(self, value):
        if isinstance(value, int):
            self.__extraction_count = value

    @property
    def faq(self):
        return self.__faq

    @faq.setter
    def faq(self, value):
        self.__faq = value

    @property
    def ref_no(self):
        return self.__ref_no

    @ref_no.setter
    def ref_no(self, value):
        if isinstance(value, basestring):
            self.__ref_no = value

    @property
    def doc_year_month(self):
        return self.__doc_year_month

    @doc_year_month.setter
    def doc_year_month(self, value):
        if isinstance(value, basestring):
            self.__doc_year_month = value


    @property
    def pack_size(self):
        return self.__pack_size

    @pack_size.setter
    def pack_size(self, value):
        if isinstance(value, list):
            self.__pack_size = value

    @property
    def assay_title(self):
        return self.__assay_title

    @assay_title.setter
    def assay_title(self, value):
        if isinstance(value, basestring):
            self.__assay_title = value

    @property
    def assay_acronym(self):
        return self.__assay_acronym

    @assay_acronym.setter
    def assay_acronym(self, value):
        if isinstance(value, basestring):
            self.__assay_acronym = value
