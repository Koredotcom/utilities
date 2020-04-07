from .languages.DefaultProcessor import DefaultProcessor as default_sent_processor
from .languages.ar.ArabicProcessor import ArabicProcessor as ar_sent_processor
from .languages.de.GermanProcessor import GermanProcessor as de_sent_processor
from .languages.en.EnglishProcessor import EnglishProcessor as en_sent_processor
from .languages.it.ItalianProcessor import ItalianProcessor as it_sent_processor
from .languages.ja.JapaneseProcessor import JapaneseProcessor as ja_sent_processor
from .languages.kk.KazakhProcessor import KazakhProcessor as kk_sent_processor
from .languages.ms.MalayProcessor import MalayProcessor as ms_sent_processor
from .languages.nl.DutchProcessor import DutchProcessor as nl_sent_processor
from .languages.pl.PolishProcessor import PolishProcessor as pl_sent_processor
from .languages.pt.PortugeseProcessor import PortugeseProcessor as pt_sent_processor
from .languages.uk.UkraineProcessor import UkraineProcessor as uk_sent_processor
from .languages.zh_cn.ChineseProcessor import ChineseProcessor as zh_cn_sent_processor
from .languages.ko.KoreanProcessor import KoreanProcessor as ko_sent_processor

text_processors = {
    'en': en_sent_processor,
    'de': de_sent_processor,
    'nl': nl_sent_processor,
    'uk': uk_sent_processor,
    'pl': pl_sent_processor,
    'ms': ms_sent_processor,
    'id': ms_sent_processor,
    'it': it_sent_processor,
    'zh_cn': zh_cn_sent_processor,
    'zh': zh_cn_sent_processor,
    'zh_tw': zh_cn_sent_processor,
    'ja': ja_sent_processor,
    'kk': kk_sent_processor,
    'ar': ar_sent_processor,
    'pt': pt_sent_processor,
    'ko': ko_sent_processor,
    'default': default_sent_processor,
}


def get_text_processor(params):
    processor = text_processors.get(params.get("lang"), text_processors.get("default"))(params)
    return processor


if __name__ == "__main__":
    params = {
        'lang': 'ko',
        'COMPOUND_WORD_SPLIT_DE': False,
        'COMPOUND_WORD_SPLIT_NL': False,
        'en_lemma': 'WORDNET',  # options: PATTERN and WORDNET,default wordnet
        'ar_lemma': 'ISRIS',  # options: SNOWBALL and ISRIS,default ISRIS
        'it_lemma': 'PATTERN',  # options: PATTERB and LOOKUP, default PATTERN
        'pt_lemma': 'RSLP',  # options: SNOWBALL and RSLP,default RSLP
    }
    l_processor = get_text_processor(params)
    sentence = "이것은 토크 나이저를 미리로드하는 것입니다"
    print(l_processor.lemma(sentence))
