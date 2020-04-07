import abc


class Processor(object, metaclass=abc.ABCMeta):
    def __init__(self, params):
        self.params = params

    @abc.abstractmethod
    def tokenize(self, doc):
        return

    @abc.abstractmethod
    def lemma(self, doc, stopwords=None):
        return

    @abc.abstractmethod
    def pos(self, sentence):
        pass

    @abc.abstractmethod
    def parse(self, sentence):
        pass
