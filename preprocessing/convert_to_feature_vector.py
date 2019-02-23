import argparse
import csv

import numpy as np
from scipy.sparse import hstack, vstack, csr_matrix
from sklearn.feature_extraction.text import CountVectorizer


def save_sparse_csr(filename, matrix):
    np.savez(filename, data=matrix.data, indices=matrix.indices, indptr=matrix.indptr, shape=matrix.shape)


def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


def get_row_words(text):
    return set(text.split(' '))


def get_all_words(infile):
    posts = csv.reader(open(infile), doublequote=False, escapechar='\\')
    
    body_words = set()
    title_words = set()
    for id, title, body, links in posts:
        try: 
            body_words.update(get_row_words(body))
            title_words.update(get_row_words(title))
        except Exception as e:
            print e
            continue
    return title_words, body_words


def convert_to_vec(infile, outfile, title_words, body_words, use_binary):
    posts = csv.reader(open(infile), doublequote=False, escapechar='\\')
    posts.next()

    i = 0
    title_vectorizer = CountVectorizer(vocabulary=title_words, binary=use_binary)
    body_vectorizer = CountVectorizer(vocabulary=body_words, binary=use_binary)    
    title_chunk = []
    body_chunk = []
    final_matrix = None
    for id, title, body, links in posts:
        title_chunk.append(title)
        body_chunk.append(body)
        if len(body_chunk) > 50000:
            try: 
                title_vec = title_vectorizer.fit_transform(title_chunk)
                body_vec = body_vectorizer.fit_transform(body_chunk)
                full_vec = hstack([title_vec, body_vec], "csr")
                if final_matrix is not None:
                    final_matrix = vstack([final_matrix, full_vec], "csr")
                else:
                    final_matrix = full_vec
                title_chunk = []
                body_chunk = []                
            except Exception as e:
                print e
                continue
        i += 1

    title_vec = title_vectorizer.fit_transform(title_chunk)
    body_vec = body_vectorizer.fit_transform(body_chunk)
    full_vec = hstack([title_vec, body_vec], "csr")
    if final_matrix is not None:
        final_matrix = vstack([final_matrix, full_vec], "csr")
    else:
        final_matrix = full_vec

    save_sparse_csr(outfile, final_matrix)
    print i, 'converted'


def convert(infile, outfile, use_binary):
    title_words, body_words = get_all_words(infile)
    print "Got vocabulary (title and body):", len(title_words), len(body_words)
    convert_to_vec(infile, outfile, sorted(title_words), sorted(body_words), use_binary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', help="posts.csv (preprocessed) location", required=True)
    parser.add_argument('-o', '--out-file', help="output file location (compressed csr matrix)", required=True)
    parser.add_argument('-b', '--binary', help="use binary feature vectors", dest='use_binary', action='store_true')

    args = parser.parse_args()

    convert(args.in_file, args.out_file, args.use_binary)
