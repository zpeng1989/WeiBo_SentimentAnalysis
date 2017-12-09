# coding:utf-8


# from __future__ import print_function
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import sys

# unicode --> utf-8
reload(sys)
sys.setdefaultencoding('utf-8')


def TxtToSet(openfile):
    with open(openfile) as f:
        corpus = f.readlines()
    f.close
    print len(corpus)
    return corpus


def bow(openfile, tag):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(TxtToSet(openfile))
    print type(X)

    Y = []
    with open(tag, 'r') as f:
        word = f.readline()
        while word:
            Y.append(word[:].replace("\n", ""))
            word = f.readline()
    f.close()
    Y = np.array(Y)
    print len(Y)

    # print X.shape,Y.shape,X[0:10000].shape,Y[0:10000].shape
    # return X[0:14870], Y, X[0:10000], Y[0:10000]
    return X[14870:]
    # return X, Y, X, Y

    # x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

    # lda = LinearDiscriminantAnalysis(n_components=10000)
    # lda.fit(np.array(x_train), y_train)
    # X_2d = lda.transform(X)
    # print X_2d

    # return x_train, y_train, x_test, y_test
    # np.save('data/train_data.npy',x_train)
    # np.save('data/test_data.npy', x_test)
    # np.save('data/y_train.npy', y_train)
    # np.save('data/y_test.npy', y_test)

# def testbow(openfile):
#     vectorizer = CountVectorizer()
#     X = vectorizer.fit_transform(TxtToSet(openfile))
#     print type(X)
#     print X
#     return  X

def Tfidf(openfile, tag):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(TxtToSet(openfile))
    transformer = TfidfTransformer(smooth_idf=False)
    tfidf = transformer.fit_transform(X)
    print type(tfidf)

    Y = []
    with open(tag, 'r') as f:
        word = f.readline()
        while word:
            Y.append(word[:].replace("\n", ""))
            word = f.readline()
    f.close()
    Y = np.array(Y)
    print len(Y)
    print tfidf.shape, Y.shape, tfidf[0:10000].shape, tfidf[0:10000].shape
    return tfidf, Y, tfidf[0:10000], Y[0:10000]


def bowofhash():
    hv = HashingVectorizer(n_features=1000)
    X = hv.transform(TxtToSet())
    print X.toarray()
    return X.toarray()


def testbowofhash():
    hv = HashingVectorizer(n_features=1000)
    X = hv.transform(TxtToSet())
    return X.toarray()[0:10000]


TxtToSet("data/seg.txt")
bow("data/seg.txt", "data/Tag.txt")
# Tfidf("data/seg.txt","data/Tag.txt")
# testbow("data/seg.txt")
# bowofhash()
# yfeature()
# testbowofhash()
# testyfeature()
# bow()
# yfeature("data/Tag.txt")
# testyfeature("data/Tag.txt")
