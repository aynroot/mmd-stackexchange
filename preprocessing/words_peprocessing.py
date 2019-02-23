"""
Remove stop words, perform stemming, remove garbage
"""

import argparse
import csv
import re

import nltk
from nltk import SnowballStemmer
from nltk import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

porter = nltk.PorterStemmer()
lancaster = nltk.LancasterStemmer()


# Tokenizing (Document to list of sentences. Sentence to list of words.)
def tokenize(str):
    '''Tokenizes into sentences, then strips punctuation/abbr, converts to lowercase and tokenizes words'''
    return  [word_tokenize(" ".join(re.findall(r'\w+', t,flags = re.UNICODE | re.LOCALE)).lower()) 
            for t in sent_tokenize(str.replace("'", ""))]


#Removing stopwords. Takes list of words, outputs list of words.
def remove_stopwords(l_words, lang='english'):
    l_stopwords = stopwords.words(lang)
    content = [w for w in l_words if w.lower() not in l_stopwords]
    return content


#Stem all words with stemmer of type, return encoded as "encoding"
def stemming(words_l, type="PorterStemmer", lang="english", encoding="utf8"):
    supported_stemmers = ["PorterStemmer","SnowballStemmer","LancasterStemmer","WordNetLemmatizer"]
    if type is False or type not in supported_stemmers:
        return words_l
    else:
        l = []
        if type == "PorterStemmer":
            stemmer = PorterStemmer()
            for word in words_l:
                l.append(stemmer.stem(word).encode(encoding))
        if type == "SnowballStemmer":
            stemmer = SnowballStemmer(lang)
            for word in words_l:
                l.append(stemmer.stem(word).encode(encoding))
        if type == "LancasterStemmer":
            stemmer = LancasterStemmer()
            for word in words_l:
                l.append(stemmer.stem(word).encode(encoding))
        if type == "WordNetLemmatizer": #TODO: context
            wnl = WordNetLemmatizer()
            for word in words_l:
                l.append(wnl.lemmatize(word).encode(encoding))
        return l

def preprocess_row(text, do_stemming):
    l = []
    sentences = tokenize(text)
    for sentence in sentences:
        words = remove_stopwords(sentence, "english")
        if do_stemming:
            words = stemming(words, "PorterStemmer")
        l.append(" ".join(words))
        # l.append(words)
    return " ".join(l)


def preprocess(infile, outfile, do_stemming):
    posts = csv.reader(open(infile), doublequote=False, escapechar='\\')
    posts_preprocessed = csv.writer(open(outfile, 'w'), doublequote=False, escapechar='\\')
    
    posts_preprocessed.writerow(['id', 'title', 'body', 'links'])
    posts.next()
    
    i = 0
    for id, title, body, links in posts:
        try: 
            preprocessed_body = preprocess_row(body.decode('utf-8'), do_stemming)
            preprocessed_title = preprocess_row(title.decode('utf-8'), do_stemming)
        except Exception as e:
            print e
            continue
        posts_preprocessed.writerow([id, preprocessed_title.encode('utf-8'), preprocessed_body.encode('utf-8'), links])
        if int(id) % 5000 == 0:
            print '.',
        i += 1

    print i, 'preprocessed'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', help="posts.csv (without html) location", required=True)
    parser.add_argument('-o', '--out-file', help="output file location", required=True)
    parser.add_argument('--stemming', choices=['on', 'off'], required=True)
    args = parser.parse_args()

    do_stemming = True if args.stemming == 'on' else False
    preprocess(args.in_file, args.out_file, do_stemming)
