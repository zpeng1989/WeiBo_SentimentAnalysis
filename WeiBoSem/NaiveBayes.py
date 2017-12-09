#coding:utf-8

from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.externals import joblib
import ForModel

def get_data():
    train_data, y_train, test_data, y_test = ForModel.bow("data/seg.txt", "data/Tag.txt")
    return train_data, y_train, test_data, y_test




def svm_train(train_data, y_train, test_data, y_test):
    # clf = MultinomialNB()
    clf = BernoulliNB()
    clf.fit(train_data, y_train)
    joblib.dump(clf, 'model/bernonb_model.pkl')
    print clf.score(test_data, y_test)






def svm_predict():
    clf = joblib.load('model/bernonb_model.pkl')

    print metrics.classification_report(y_test, clf.predict(test_data))

train_data,y_train,test_data,y_test = get_data()
svm_train(train_data, y_train, test_data, y_test)
svm_predict()
