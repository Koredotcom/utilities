from LanguageModel.Processor import Processor


class ChineseProcessor(Processor):
    def tokenize(self, doc):
        tokens = []
        temp = ""
        for charecter in doc:
            if charecter > u'\u4e000' and charecter < u'\u9fff':
                if temp != "":
                    tokens.extend(temp.strip().split(" "))
                    temp = ""
                tokens.append(charecter)
            else:
                temp += str(charecter)
        if temp != "":
            tokens.extend(temp.strip().split(" "))
        tokens = [token for token in tokens if not token == ""]
        return tokens

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
