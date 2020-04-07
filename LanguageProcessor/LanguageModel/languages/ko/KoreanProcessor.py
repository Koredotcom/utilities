from konlpy.tag import Mecab

from ...Processor import Processor
from ...config import MECAB_KO_DIR

if MECAB_KO_DIR:
    print('mecab dir present -- {}'.format(MECAB_KO_DIR))
    mecab = Mecab(MECAB_KO_DIR)


class KoreanProcessor(Processor):
    def tokenize(self, doc):
        tokens = mecab.pos(doc)
        return tokens

    def lemma(self, doc, stopwords=None):
        tokens = self.tokenize(doc)
        lemma_list = list()
        for token_tuple in tokens:
            result = dict()
            result['lemma'] = token_tuple[0]
            result['pos'] = token_tuple[1]
            lemma_list.append(result)
        return tokens

    def parse(self, sentence):
        pass

    def pos(self, sentence):
        pass


if __name__ == "__main__":
    k_p = KoreanProcessor({'lang': 'ko'})
    doc = "이것은 토크 나이저를 미리로드하는 것입니다"
    print(k_p.lemma(doc))