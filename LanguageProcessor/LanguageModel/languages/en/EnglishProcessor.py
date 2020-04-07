import json

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from pattern.en import lemma as lemma_en

from LanguageModel.Processor import Processor

wnl = WordNetLemmatizer()
wordnet.ensure_loaded()
stemmer = SnowballStemmer('english')
language_code = 'en'


def read_file(filename):
    try:
        with open(filename, "r") as file_dp:
            data = json.load(file_dp)
            return data
    except Exception:
        return {}


class Singleton(object):
    """
    Singleton interface:
    http://www.python.org/download/releases/2.2.3/descrintro/#__new__
    """

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass


class EnglishDict(Singleton):
    def init(self):
        self.en_dictionary = self.load_en_dictionary()

    def load_en_dictionary(self):
        try:
            a = read_file("languages/en/english_dictionary.json")
            print('English dictionary loaded')
            return a
        except:
            print('ERROR: english dictionary for pattern lemma not loaoded')
            return dict()

    def is_english_word(self, word):
        try:
            x = self.en_dictionary[word.lower()]
            return True
        except KeyError:
            return False


en_dict = EnglishDict()


class EnglishProcessor(Processor):

    def tokenize(self, doc):
        return word_tokenize(doc, language=language_code)

    def english_lemmatizer(self, tokens):
        """ english lemma"""
        lemma_list = []
        english_edit = {'banking': 'bank', 'us': 'us', 'timing': 'time', 'timings': 'time'}
        for word in tokens:
            lowercase_word = word.lower()
            if lowercase_word in english_edit:
                lemma_list.append(english_edit[lowercase_word])
            elif en_dict.is_english_word(lowercase_word):
                lemma_list.append(lemma_en(lowercase_word))
            else:
                lemma_list.append(lowercase_word)
        return [{'lemma': word, 'pos': ''} for word in lemma_list]

    @staticmethod
    def _get_wordnet_pos_lem(token, tree_bank_tag):
        pos = None
        if tree_bank_tag.startswith('J'):
            pos = wordnet.ADJ
        elif tree_bank_tag.startswith('V'):
            pos = wordnet.VERB
        elif tree_bank_tag.startswith('N'):
            pos = wordnet.NOUN
        elif tree_bank_tag.startswith('R'):
            pos = wordnet.ADV

        if pos:
            return wnl.lemmatize(token, pos)
        else:
            return wnl.lemmatize(token)

    def wordnet_lemma_helper(self, tokens, stopwords):
        tokens_pos_tags = pos_tag(tokens)
        pos_tagged_tokens = list(zip(tokens, tokens_pos_tags))
        features = [
            {'lemma': stemmer.stem(self._get_wordnet_pos_lem(t, tag[1])), 'pos': tag[1]} if not tag[1].startswith('N')
            else {'lemma': self._get_wordnet_pos_lem(t, tag[1]), 'pos': tag[1]} if t not in stopwords else t
            for t, tag in pos_tagged_tokens]

        return features

    def lemma(self, doc, stopwords=None):
        if stopwords is None:
            stopwords = list()
        tokens = self.tokenize(doc)
        if self.params.get('en_lemma', '') == 'PATTERN':
            return self.english_lemmatizer(tokens)
        else:
            return self.wordnet_lemma_helper(tokens, stopwords)

    def pos(self, sentence):
        pass

    def parse(self, sentence):
        pass


if __name__ == '__main__':
    n = EnglishProcessor({})
    print(n.lemma("i am working in kore.ai don't have children timings"))
