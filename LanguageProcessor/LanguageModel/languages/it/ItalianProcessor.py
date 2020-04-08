import pickle
import traceback

from LanguageModel.Processor import Processor
from LanguageModel.common import SUPPORTED_LANGUAGES
from nltk import word_tokenize
from pattern.it import lemma as lemma_it

dirpath = __file__[:__file__.rfind("/")]

try:
    with open(dirpath + '/lemma_it.pkl', 'rb') as fp:
        lemmatizer_dict = pickle.load(fp)
except:
    print(traceback.format_exc())
    print("ERROR: Italian Lemma list is not loaded!, is this expected ?")
    lemmatizer_dict = {}



class ItalianProcessor(Processor):

    def tokenize(self, doc):
        return word_tokenize(doc, language=SUPPORTED_LANGUAGES[self.params.get('lang', 'it')])

    def lemma(self, doc, stopwords=None):
        lemma_tokens = list()
        word_tokens = self.tokenize(doc)
        if self.params.get('it_lemma', 'PATTERN') == 'LOOKUP':
            for word in word_tokens:
                result = dict()
                result['lemma'] = lemmatizer_dict.get(word, word)
                result['pos'] = ''
                lemma_tokens.append(result)
        else:
            for word in word_tokens:
                result = dict()
                result['lemma'] = lemma_it(word)
                result['pos'] = ''
                lemma_tokens.append(result)
        return lemma_tokens

    def pos(self, sentence):
        pass

    def parse(self, sentence):
        pass


if __name__ == "__main__":
    k_p = ItalianProcessor({'lang': 'it'})
    doc = "this is italina"
    print(k_p.lemma(doc))
