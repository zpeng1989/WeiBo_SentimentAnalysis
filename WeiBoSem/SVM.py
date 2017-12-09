#coding:utf-8

from sklearn import metrics
from sklearn.svm import SVC
import  numpy as np
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
import ForModel

def get_data():
    # train_data = np.load('data/train_data.npy')
    # y_train = np.load('data/y_train.npy')
    # test_data = np.load('data/test_data.npy')
    # y_test = np.load('data/y_test.npy')
    train_data, y_train, test_data, y_test = ForModel.bow("data/seg.txt","data/Tag.txt")
    # train_data, y_train, test_data, y_test = ForModel.Tfidf("data/seg.txt", "data/Tag.txt")
    return train_data, y_train, test_data, y_test


# 训练svm模型

def svm_train(train_data, y_train, test_data, y_test):
    clf = SVC(kernel='linear',verbose=True)
    clf.fit(train_data, y_train)
    joblib.dump(clf, 'model/svm_model.pkl')
    print clf.score(test_data, y_test)




# 对单个句子进行情感判断

def svm_predict():
    clf = joblib.load('model/svm_model.pkl')

    print metrics.classification_report(y_test, clf.predict(test_data))

train_data,y_train,test_data,y_test = get_data()
svm_train(train_data, y_train, test_data, y_test)
svm_predict()
