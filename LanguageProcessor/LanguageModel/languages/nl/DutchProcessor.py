from LanguageModel.Processor import Processor
from LanguageModel.common import read_file
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

language_code = 'nl'
language = 'dutch'
stemmer = SnowballStemmer(language)

nl_compound_word_map = read_file("nl_compound_words.json")

'''
Required configuration params 
{
    COMPOUND_WORD_SPLIT_NL: bool,
}
'''


class DutchProcessor(Processor):
    def tokenize(self, doc):
        return word_tokenize(doc, language=language)

    def break_compund_words(self, tokens):
        if not self.params.get('COMPOUND_WORD_SPLIT_NL', False):
            return tokens

        doc = list()
        for word in tokens:
            if word in nl_compound_word_map:
                try:
                    doc.extend(nl_compound_word_map[word].replace("+", "||").replace("_", "||").replace(" ",
                                                                                                        "").split("||"))
                except:
                    doc.append(word)
            else:
                doc.append(word)
        return doc

    def lemma(self, doc, stopwords=None):
        if not stopwords:
            stopwords = list()
        lemma_list = list()
        word_tokens = self.tokenize(doc)
        compound_split_tokens = self.break_compund_words(word_tokens)
        compound_split_sentence = ' '.join(compound_split_tokens)
        for word in self.tokenize(compound_split_sentence):
            result = dict()
            result['lemma'] = stemmer.stem(word) if word not in stopwords else word
            result['pos'] = ''
            lemma_list.append(result)
        return lemma_list

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass


if __name__ == '__main__':
    d_p = DutchProcessor({})
    print(d_p.lemma('ik heb een wiebelende vuursteengeweer tap'))
