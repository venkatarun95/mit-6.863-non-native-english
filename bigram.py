#!/bin/python

import hashlib
import inspect
import math
import nltk
import os
import pickle
import sys
import time

def admissible_ngram(ngram):
    '''Returns an admissible ngram if possible. Else returns None.'''
    if len(ngram) == 0:
        return ''

    c = ngram[0]
    res = None
    if c.isalpha():
        res = c.lower()
    elif c.isspace():
        res = ' '
    elif c in ['-', ',', '.']:
        res = c
    else:
        return None

    x = admissible_ngram(ngram[1:])
    if x is None:
        return None
    return res + x

def memoize(function, filename):
    '''Warning: This cannot detect if any functions called by `function` have
    changed

    '''
    def hash(x):
        return hashlib.sha224(x.encode('utf-8')).hexdigest()
    function_hash = hash(inspect.getsource(function)) # hashlib.sha224(inspect.getsource(function).encode('utf-8')).hexdigest()
    filename = os.path.abspath(filename)
    pickle_filename = '/tmp/%s' % hash(filename + function_hash)
    print(pickle_filename, function_hash)
    mtime = os.path.getmtime(filename)

    if os.path.isfile(pickle_filename):
        try:
            with open(pickle_filename, 'rb') as f:
                data = pickle.load(f)
                if data[0][0] >= mtime and data[0][1] == function_hash:
                    print("Using memoized file %s" % pickle_filename)
                    return data[1]
        except:
            pass

    with open(filename) as f:
        print("Computing afresh")
        res = function(f)
        with open(pickle_filename, 'wb') as f:
            pickle.dump(((mtime, function_hash), res), f)
        return res

def get_file_ngrams(f, n=2):
    ngrams = {}
    for line in f.readlines():
        for i in range(n-1, len(line)):
            x = admissible_ngram(line[i-n+1:i+1])
            if x is None:
                continue
            if x not in ngrams:
                ngrams[x] = 1
            else:
                ngrams[x] += 1
    return ngrams

def get_file_pos_ngrams(f, n=3):
    ngrams = {}
    for line in f.readlines():
        line = line[:-1]
        if not line.isprintable():
            continue
        pos = nltk.pos_tag(nltk.word_tokenize(line))
        for i in range(n-1, len(pos)):
            ngram = '-'.join([x[1] for x in pos[i-n+1:i+1]])
            if not ngram in ngrams:
                ngrams[ngram] = 1
            else:
                ngrams[ngram] += 1
    return ngrams

def run_t_test(a, b, t_thresh = 1.96):
    # Default t_thresh corresponds to 95% confidence in two-sided t-test with
    # infinite degrees of freedom
    atot = sum(a.values())
    btot = sum(b.values())
    res = {}
    #assert(btot > atot)
    for key in a:
        if key not in b:
            continue
        if a[key] <= 10 or b[key] <= 10:
            continue
        amean = 1.0 * a[key] / atot
        bmean = 1.0 * b[key] / btot
        avar = amean * (1. - amean)
        bvar = bmean * (1. - bmean)
        t = (amean - bmean) / math.sqrt(avar / atot + bvar / btot)
        #t = (amean - bmean) / math.sqrt(avar / atot)
        if abs(t) > t_thresh:
            res[key] = t
    return res

if __name__ == "__main__":
    natives = memoize(get_file_pos_ngrams, 'ENNTT/natives.tok')
    for fname in sys.argv[1:]:
        file_ngrams = memoize(get_file_pos_ngrams, fname)
        print(fname)
        t_test = run_t_test(file_ngrams, natives, 3.291)
        print(t_test, len(t_test.keys()))
