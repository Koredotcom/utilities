from LanguageModel.Processor import Processor
from LanguageModel.common import *
from nltk import word_tokenize, SnowballStemmer


class DefaultProcessor(Processor):
    def tokenize(self, doc):
        language = self.params.get('lang')
        if language in PUNKT_SUPPORT:
            return word_tokenize(doc, language=SUPPORTED_LANGUAGES[language])
        return word_tokenize(doc)

    def lemma(self, doc, stopwords=None):
        tokens = self.tokenize(doc)
        if self.params.get('lang') in SNOWBALL_SUPPORT:
            stemmer = SnowballStemmer(SUPPORTED_LANGUAGES[self.params.get('lang')])
            return [stemmer.stem(word) for word in tokens]
        return tokens

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass
