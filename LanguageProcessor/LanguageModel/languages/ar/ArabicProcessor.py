from nltk import word_tokenize
from nltk.stem.isri import ISRIStemmer
from nltk.stem.snowball import SnowballStemmer

from ...Processor import Processor

language = 'arabic'
sn_stemmer = SnowballStemmer(language)
isris_stemmer = ISRIStemmer()


class ArabicProcessor(Processor):
    def tokenize(self, doc):
        return word_tokenize(doc)

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
        if self.params.get('ar_lemma', 'ISRIS') == 'SNOWBALL':
            return self._lemma_helper(tokenized_sent, sn_stemmer.stem)
        else:
            return self._lemma_helper(tokenized_sent, isris_stemmer.stem)

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass


if __name__ == "__main__":
    params = {'lang': 'en', 'ar_lemma': ''}
    a_p = ArabicProcessor(params)
    print(a_p.lemma("اين تعمل؟"))
