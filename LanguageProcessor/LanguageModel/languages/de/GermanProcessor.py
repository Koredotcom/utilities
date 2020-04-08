from LanguageModel.Processor import Processor
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

from LanguageModel.common import SUPPORTED_LANGUAGES

try:
    import LanguageDetection

    LANG_DETECT_AVAILABLE = True
except:
    print('Error in importing LanguageDetection module')
    LANG_DETECT_AVAILABLE = False

language_code = 'de'
stemmer = SnowballStemmer(SUPPORTED_LANGUAGES[language_code])

'''
Required configuration params 
{
    COMPOUND_WORD_SPLIT_DE: bool,
}
'''


class GermanProcessor(Processor):
    def tokenize(self, doc):
        return word_tokenize(doc, language=SUPPORTED_LANGUAGES[language_code])

    def break_compund_words(self, sentence):
        if not self.params.get('COMPOUND_WORD_SPLIT_DE', False):
            return sentence
        else:
            if LANG_DETECT_AVAILABLE:
                try:
                    sentence, _ = LanguageDetection.split_compound(sentence, language_code)
                except:
                    pass
            return sentence

    def lemma(self, doc, stopwords=None):
        if not stopwords:
            stopwords = list()
        compound_split_sentence = self.break_compund_words(doc)
        lemma_tokens = list()
        for word in self.tokenize(compound_split_sentence):
            result = dict()
            result['lemma'] = stemmer.stem(word) if word not in stopwords else word
            result['pos'] = ''
            lemma_tokens.append(result)
        return lemma_tokens

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass
