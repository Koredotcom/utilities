from mosestokenizer import MosesTokenizer

from ...Processor import Processor
from .kazlemmatizer import KazakhLemmatizer

kazakh_lemmatizer = KazakhLemmatizer()


class KazakhProcessor(Processor):
    def tokenize(self, doc):
        with MosesTokenizer('kk') as tokenize:
            tokens = tokenize(doc)
        return tokens

    def lemma(self, doc, stopwords=None):
        if not stopwords:
            stopwords = list()
        lemma_tokens = list()
        tokenized_sent = self.tokenize(doc)
        for token in tokenized_sent:
            result = dict()
            if token not in stopwords:
                result['lemma'] = kazakh_lemmatizer.lemmatize(token)
            else:
                result['lemma'] = token
            result['pos'] = ''
            lemma_tokens.append(result)

        return lemma_tokens

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass
