from nltk import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.stem.snowball import SnowballStemmer

from LanguageModel.Processor import Processor
from LanguageModel.common import SUPPORTED_LANGUAGES

language_code = 'pt'
stem_pt = RSLPStemmer()
snowball_pt_stemmer = SnowballStemmer(SUPPORTED_LANGUAGES[language_code])


class PortugeseProcessor(Processor):
    def tokenize(self, doc):
        return word_tokenize(doc, language=SUPPORTED_LANGUAGES[language_code])

    def _lemma_helper(self, tokenized_sent, lemma):
        lemma_tokens = list()
        for word in tokenized_sent:
            result = dict()
            result['lemma'] = lemma(word)
            result['pos'] = ''
            lemma_tokens.append(result)
        return lemma_tokens

    def lemma(self, doc, stopwords=None):
        tokenized_sent = self.tokenize(doc)
        if self.params.get('lemma', 'RSLP') == 'SNOWBALL':
            return self._lemma_helper(tokenized_sent, snowball_pt_stemmer.stem)
        else:
            return self._lemma_helper(tokenized_sent, stem_pt.stem)

    def pos(self, sentence):
        pass

    def parse(self, sentence):
        pass
