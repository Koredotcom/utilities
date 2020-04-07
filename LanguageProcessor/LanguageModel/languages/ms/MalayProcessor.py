from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from LanguageModel.Processor import Processor

factory = StemmerFactory()
stemmer = factory.create_stemmer()


class MalayProcessor(Processor):
    def tokenize(self, doc):
        pass

    def lemma(self, doc, stopwords=None):
        stemmer_result = stemmer.stem(doc).split()
        result = [{'lemma': word, 'pos': ''} for word in stemmer_result]
        return result

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass
