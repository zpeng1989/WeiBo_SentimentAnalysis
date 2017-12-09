# coding:utf-8

from sklearn import metrics
from sklearn.svm import SVC
import numpy as np
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
import ForModel
import matplotlib.pyplot as plt


def get_data():
    # train_data = np.load('data/train_data.npy')
    # y_train = np.load('data/y_train.npy')
    # test_data = np.load('data/test_data.npy')
    # y_test = np.load('data/y_test.npy')
    train_data, y_train, test_data, y_test = ForModel.bow("data/segnonull.txt", "data/Tagnonull.txt")
    # train_data, y_train, test_data, y_test = ForModel.Tfidf("data/seg.txt", "data/Tag.txt")
    return train_data, y_train, test_data, y_test


def get_data_test():
    test_data = ForModel.bow("data/segnonull.txt", "data/Tagnonull.txt")
    print test_data
    return test_data


# 训练svm模型

def svm_train(train_data, y_train, test_data, y_test):
    clf = SVC(kernel='linear', verbose=True)
    clf.fit(train_data, y_train)
    joblib.dump(clf, 'model/svm_model_nonull.pkl')
    print clf.score(test_data, y_test)


# 对单个句子进行情感判断

def svm_predict():
    clf = joblib.load('model/svm_model_nonull.pkl')
    # test_data = ForModel.testbow("data/1_segtest.txt")
    # print test_data

    Y = clf.predict(test_data)

    likecount = 0
    angercount = 0
    disgustcount = 0
    happinesscount = 0
    fearcount = 0
    sadnesscount = 0
    for y in Y:
        if (y == "like"):
            likecount = likecount + 1
        elif (y == "anger"):
            angercount = angercount + 1
        elif (y == "disgust"):
            disgustcount = disgustcount + 1
        elif (y == "happiness"):
            happinesscount = happinesscount + 1
        elif (y == "fear"):
            fearcount = fearcount + 1
        elif (y == "sadness"):
            sadnesscount = sadnesscount + 1
    print "likecount:", likecount
    print "angercount:", angercount
    print "disgustcount:", disgustcount
    print "happinesscount:", happinesscount
    print "fearcount:", fearcount
    print "sadnesscount:", sadnesscount
    print "total:", likecount + angercount + disgustcount + happinesscount + fearcount + sadnesscount

    pos = likecount + happinesscount
    neg = angercount + fearcount + sadnesscount + disgustcount

    # labels1 = ['like', 'anger', 'disgust', 'happiness', 'sadness', 'fear']
    # X = [likecount, angercount, disgustcount, happinesscount, sadnesscount, fearcount]
    # fig = plt.figure()
    # plt.pie(X, labels=labels1, autopct='%1.2f%%',startangle=90)
    # plt.bar(range(len(X)), X, tick_label=labels1, color='rbg')
    # plt.show()

    labels2 = ['positive', 'negative']
    X = [pos, neg]
    fig = plt.figure()
    # plt.pie(X, labels=labels2, autopct='%1.2f%%', startangle=90)
    plt.bar(range(len(X)), X, tick_label=labels2, color='rbg',width=0.2)
    plt.show()

    # print metrics.classification_report(y_test, clf.predict(test_data))



test_data = get_data_test()
# train_data, y_train, test_data, y_test = get_data()
# svm_train(train_data, y_train, test_data, y_test)
svm_predict()
