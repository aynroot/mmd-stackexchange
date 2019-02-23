import argparse
import pickle
import csv
import numpy as np

from os.path import isfile
from sparselsh import LSH
from scipy.sparse import csr_matrix
from sklearn.cross_validation import ShuffleSplit


def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


def find_nearest_neighbors(in_file, out_file, path_to_table, num_test, random_seed, hash_size, num_neighbors):
    posts = load_sparse_csr(args.in_file)
    num_samples, num_dimensions = posts.shape

    # Train / test split
    train_index, test_index = next(iter(ShuffleSplit(num_samples, n_iter=1, test_size=num_test, random_state=random_seed)))

    # Load or create the LSH table object
    if path_to_table:
        if isfile(path_to_table):
            lsh = pickle.load(open(path_to_table))
            print('LSH table loaded')
        else:
            raise Exception("LSH table doesn't exist")
    else:
        lsh = LSH(args.hash_size,
                  num_dimensions,
                  num_hashtables=1,
                  storage_config={"dict": None})

        # Both the train and test posts are included, so that saving the output is easier 
        # and the table can be stored and used for any train/test split
        for ix in xrange(num_samples):
            x = posts.getrow(ix)    
            lsh.index(x, extra_data=ix)

        print('LSH table constructed')

        # Dump the table, so that it can be reused later
        pickle.dump(lsh, open('lsh_table', 'w'))

    # Perform the nearest neighbor search for each of the samples in the test set
    nearest_neighbors = dict()
    for ix in test_index:
        neighbors = lsh.query(posts.getrow(ix))
        # The closest element is always the element itself, so need to iterate to num_neighbors + 1
        nearest_neighbors[ix] = [neighbors[i][0][1] for i in range(num_neighbors + 1)]

    print('Nearest neighbors found')

    # Save the results to csv
    nn_file = csv.writer(open(out_file, 'w'), doublequote=False, escapechar='\\')
    nn_file.writerow(['id'] + ['n{}'.format(i) for i in range(1, num_neighbors + 1)])
    for row in nearest_neighbors.itervalues():
        nn_file.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--in-file', help="posts matrix file location", required=True)
    parser.add_argument('-o', '--out-file', help="name of the output file", required=True)

    # The LSH table takes a lot of time to compute, so it's more efficient to store it in a file with pickle
    parser.add_argument('-t', '--table', help="location of the pickled LSH table, table is computed anew if not specified", default=False)
    parser.add_argument('--hash-size', help="size of bits for the hash, more means higher accuracy (allegedly), but also higher runtime", type=int, default=8)
    parser.add_argument('--seed', help="random seed for the test/train split, specify for reproducible results", type=int, default=123)
    parser.add_argument('--num-test', help="number of posts to put in the test set", type=int, default=100)
    parser.add_argument('--num-neighbors', help="number of closest neigbors to store in the output file", type=int, default=10)
    args = parser.parse_args()

    find_nearest_neighbors(args.in_file, args.out_file, args.table, args.num_test, args.seed, args.hash_size, args.num_neighbors)
