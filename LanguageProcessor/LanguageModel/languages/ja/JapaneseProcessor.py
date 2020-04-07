import tinysegmenter

from ...Processor import Processor

stem_ja = tinysegmenter.TinySegmenter()


class JapaneseProcessor(Processor):
    def tokenize(self, doc):
        return stem_ja.tokenize(doc)

    def lemma(self, doc, stopwords=None):
        lemma_tokens = list()
        tokenized_sent = self.tokenize(doc)
        for word in tokenized_sent:
            result = dict()
            result['lemma'] = word
            result['pos'] = ''
            lemma_tokens.append(result)
        return lemma_tokens

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass
