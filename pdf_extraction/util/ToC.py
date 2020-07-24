# -*- coding: utf-8 -*-


import re
import unicodedata

import unidecode
from PyPDF2 import PdfFileReader


def char_filter(string):
    latin = re.compile('[a-zA-Z]+')
    for char in unicodedata.normalize('NFC', string):
        decoded = unidecode.unidecode(char)
        if latin.match(decoded):
            yield char
        else:
            yield decoded


def clean_string(string):
    if not isinstance(string, str):
        return string
    return "".join(char_filter(string))


def flatten_toc(toc_pypdf2, flattened_toc, level, reader):
    if isinstance(toc_pypdf2, list):
        for element in toc_pypdf2:
            flattened_toc = flatten_toc(element, flattened_toc, level + 1, reader)
    else:
        toc_pypdf2_str = str(toc_pypdf2)
        start = "'/Page': IndirectObject("
        end = ", 0)"
        toc_pypdf2_page = (toc_pypdf2_str.split(start))[1].split(end)[0]
        flattened_toc.append(
            (clean_string(toc_pypdf2['/Title']), reader._getPageNumberByIndirect(int(toc_pypdf2_page)), level))
    return flattened_toc


def clean_extracted_toc(toc):
    new_toc = []
    for element in toc:
        (text, page_no, level) = element
        cleaned_text = clean_string(text)
        cleaned_text = cleaned_text.replace('"', "'")
        new_toc.append((cleaned_text, page_no, level))
    return new_toc


def get_toc(filename):
    reader = PdfFileReader(open(filename, 'rb'))
    toc_pypdf2 = reader.outlines
    flattened_toc = []
    flattened_toc = flatten_toc(toc_pypdf2, flattened_toc, 0, reader)
    flattened_toc = clean_extracted_toc(flattened_toc)
    # if DEBUG_PRINT_FLATTENED_TOC:
    # print('TOC : ' + str(flattened_toc))
    return [i[0] for i in flattened_toc]


if __name__ == "__main__":
    file_name = ""
    for i in range(12, 14):
        file_name = "/home/satyaaditya/Downloads/roche version num docs/" + str(i) + ".pdf"
        result_ = get_toc(file_name)
        print result_