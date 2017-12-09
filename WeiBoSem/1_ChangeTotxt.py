# -*- coding: UTF-8 -*-

from xml.dom.minidom import parse
import  xml.dom.minidom
import matplotlib.pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#使用mindom解析器打开xml文档
DOMTree = xml.dom.minidom.parse("data/Training data for Emotion Classification.xml")
collection = DOMTree.documentElement

#在集合中获取所有微博
weibos = collection.getElementsByTagName("weibo")


def xmlTotxt():
    nullcount = 0
    likecount = 0
    angercount = 0
    disgustcount = 0
    happinesscount = 0
    fearcount = 0
    sadnesscount = 0
    with open("data/train.txt",'w') as f:
        for weibo in weibos:
            sentences = weibo.getElementsByTagName("sentence")
            for sentence in sentences:
                if sentence.hasAttribute("emotion-1-type"):
                    # if (sentence.getAttribute("emotion-1-type") == "anger"):
                    #     f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    #     f.write("\n")
                    # elif(sentence.getAttribute("emotion-1-type") == "disgust"):
                    #     f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    #     f.write("\n")
                    # elif (sentence.getAttribute("emotion-1-type") == "fear"):
                    #     f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    #     f.write("\n")
                    # elif (sentence.getAttribute("emotion-1-type") == "sadness"):
                    #     f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    #     f.write("\n")
                    # else:
                    #     pass
                    # else :
                    #     f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    #     f.write("\n")
                    f.write(sentence.getAttribute("emotion-1-type") + " " + sentence.childNodes[0].data)
                    f.write("\n")
                    if(sentence.getAttribute("emotion-1-type") == "like"):
                        likecount += 1
                    if (sentence.getAttribute("emotion-1-type") == "anger"):
                        angercount += 1
                    if (sentence.getAttribute("emotion-1-type") == "disgust"):
                        disgustcount += 1
                    if (sentence.getAttribute("emotion-1-type") == "happiness"):
                        happinesscount += 1
                    if (sentence.getAttribute("emotion-1-type") == "fear"):
                        fearcount += 1
                    if (sentence.getAttribute("emotion-1-type") == "sadness"):
                        sadnesscount += 1
                else:
                    f.write("null" + ' ' +sentence.childNodes[0].data)
                    f.write("\n")
                    nullcount += 1

    f.close
    labels1 = ['null','like','anger','disgust','happiness','sadness','fear']
    X = [nullcount,likecount,angercount,disgustcount,happinesscount,sadnesscount,fearcount]
    fig = plt.figure()
    plt.pie(X,labels=labels1,autopct='%1.2f%%')
    plt.title("weibo sam data")
    labels2 = [ 'like', 'anger', 'disgust', 'happiness', 'sadness', 'fear']
    Y = [ likecount, angercount, disgustcount, happinesscount, sadnesscount, fearcount]
    fig = plt.figure()
    plt.pie(Y, labels=labels2, autopct='%1.2f%%')
    plt.title("weibo sam data without null")
    plt.show()


    print "null:" , nullcount
    print "like:" , likecount
    print "anger:" , angercount
    print "disgust:" , disgustcount
    print "happiness:" , happinesscount
    print "sadness:" , sadnesscount
    print "fear:" , fearcount
xmlTotxt()