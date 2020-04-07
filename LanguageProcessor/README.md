## Kore-Langauge-Processor
This libraries provide utilities required for text processing in both ML and FAQ engines

### Usage
```
    from LanguageProcessor.LanguageModel import TextProcessor
    sample_params = {
        'lang': 'en'
    }
    text_processor = get_text_processor(params)
    sentence = "This is banking application for children"
    print(text_processor.lemma(sentence))
```
#####Output
Output object contains two keys for each word, lemmatized form of word and pos-tag of word if available
```[{'lemma': 'this', 'pos': 'DT'}, {'lemma': 'be', 'pos': 'VBZ'}, {'lemma': 'bank', 'pos': 'VBG'}, {'lemma': 'application', 'pos': 'NN'},{'lemma': 'for', 'pos': 'IN'}, {'lemma': 'child', 'pos': 'NNS'}]```

###Parameters Used

param | values | default value|
:---: | :---: | :---:|
|lang | language_code| no default value | 
|COMPOUND_WORD_SPLIT_DE| [True, False]| False
|COMPOUND_WORD_SPLIT_NL| [True, False]| False
|en_lemma|['WORDNET', 'PATTERN']| WORDNET
|ar_lemma|['SNOWBALL', 'ISRIS']|ISRIS
|it_lemma|['PATTERN', 'LOOKUP']|PATTERN
|pt_lemma|['SNOWBALL', 'RSLP']|RSLP

#### Values functionality

|value| behaviour|
|:---:|:---:|
|LOOKUP| lemmatizes using a default map, where each word is mapped to its lemma form|
|WORDNET| Does lemmatization using NLTK Wordnet module
|PATTERN| Does lemmatization using pattern module
|SNOWBALL| Does stemming using NLTK Snowball stemmer
|ISRIS| Does stemming using sastrawi ISRIS stemmer
|RSLP| Does stemming using RSLP stemmer
|COMPOUND_WORD_SPLIT_DE| Set it to true to use compound word splitting in german
|COMPOUND_WORD_SPLIT_NL| Set it to true to use compound word splitting in Dutch

###Lemmatizers and postagger availability 

|language_code| processor| Pos tagger
|:---:|:---:|:---:
en|lemma |available
de|stemmer| NA
fr|stemmer| NA
nl|stemmer| NA
ar|stemmer| NA
it|lemma_lookup |NA
ja|tokenizer|NA
kk| lemma | NA
pl| lemma_lookup| NA
pt| stemmer| NA
uk| lemma_lookup| NA
ms| stemmer| NA
sv| stemmer| NA
ko|tokenizer|NA
fi|stemmr|NA
zh,zh_cn,zh_tw| tokeinizer| NA

