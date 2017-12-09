#coding:utf-8

from __future__ import print_function
import jieba
import jieba.posseg as pseg
import  sys
#unicode --> utf-8
reload(sys)
sys.setdefaultencoding('utf-8')
#做一个没有标记的文档 待会拿来分词
def TotalDoc(openfile,writefile):
    with open(openfile) as f:
        #with open("train.txt") as f:
        word = f.readline()
        with open(writefile,'w') as w:
            # with open("ForSeg.txt", 'w') as w:
            while word:
                #变成list
                Forseg = word.strip().split(' ')
                w.write(Forseg[1])
                w.write("\n")
                word = f.readline()
        w.close()
    f.close()

#单独的所有标签
def TotalTag(openfile,writefile):
    with open(openfile) as f:
        # with open("train.txt") as f:
        word = f.readline()
        with open(writefile,'w') as w:
            # with open("Tag.txt", 'w') as w:
            while word:
                #变成list
                Forseg = word.strip().split(' ')
                w.write(Forseg[0])
                w.write("\n")
                word = f.readline()
        w.close()
    f.close()

#利用jieba做中文分词
def Seg(openfile,writefile):
    with open(openfile) as f:
        # with open("ForSeg.txt") as f:
        line = f.readline()
        with open(writefile,'w') as w:
            # with open("seg.txt", 'w') as w:
            while line:
                seg_list = jieba.cut(line)
                w.write("  ".join(seg_list))
                line = f.readline()
        w.close()
    f.close()


def SegNoStopWord(openfile,writefile):
    stopword = ['@',':','，','/','_','。','[',']','、','了','（','）','＝',
                '～','；','...','！','?','／','..','？',',','!','—','~','》','《','：',
                '......',';','|','…','.','「','」','-','(',')','［','］','〈','〉','^','＂']
    with open(openfile) as f:
        # with open("ForSeg.txt") as f:
        line = f.readline()
        with open(writefile,'w') as w:
            # with open("segnostopword.txt", 'w') as w:
            while line:
                seg_list = jieba.cut(line)
                for word in seg_list:
                    if word not in stopword:
                        w.write(word.strip())
                        w.write(" ")
                w.write("\n")
                line = f.readline()
        w.close()
    f.close()

def pos():
    with open("segnostopword.txt") as f:
        line = f.readline()
        line = line.replace(" ","")
        words = pseg.cut(line)
        for flag in words:
            print  (flag,end = ' ')

# TotalDoc("data/train.txt","data/ForSeg.txt")
# TotalDoc("data/trainnonull.txt","data/ForSegNoNull.txt")
# TotalDoc("data/trainneg.txt","data/ForSegneg.txt")
# TotalDoc("data/trainpos.txt","data/ForSegpos.txt")

# TotalTag("data/train.txt","data/Tag.txt")
# TotalTag("data/trainnonull.txt","data/Tagnonull.txt")
# TotalTag("data/trainneg.txt","data/Tagneg.txt")
# TotalTag("data/trainpos.txt","data/Tagpos.txt")

# Seg("data/ForSeg.txt","data/seg.txt")
# Seg("data/ForSegNoNull.txt","data/segnonull.txt")
# Seg("data/ForSegneg.txt","data/segneg.txt")
# Seg("data/ForSegpos.txt","data/segpos.txt")


# SegNoStopWord("data/ForSeg.txt","data/sw_seg.txt")
# SegNoStopWord("data/ForSegNoNull.txt","data/sw_segnonull.txt")
# SegNoStopWord("data/ForSegneg.txt","data/sw_segneg.txt")
# SegNoStopWord("data/ForSegpos.txt","data/sw_segpos.txt")