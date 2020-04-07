import pickle
import traceback

from nltk import word_tokenize

from ...Processor import Processor

dirpath = __file__[:__file__.rfind("/")]

try:
    with open(dirpath + '/lemma_uk.pkl', 'rb') as fp:
        lemmatizer_dict = pickle.load(fp)
except:
    print(traceback.format_exc())
    print("ERROR: Ukranian Lemma list is not loaded!, is this expected ?")
    lemmatizer_dict = {}


class UkraineProcessor(Processor):

    def tokenize(self, doc):
        return word_tokenize(doc)

    def lemma(self, doc, stopwords=None):
        lemma_tokens = list()
        for word in self.tokenize(doc):
            result = dict()
            result['lemma'] = lemmatizer_dict.get(word, word)
            result['pos'] = ''
            lemma_tokens.append(result)
        return lemma_tokens

    def pos(self, sentence):
        pass

    def parse(self, sentence):
        pass
