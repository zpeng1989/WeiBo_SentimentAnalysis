# WeiBo_SentimentAnalysis


数据挖掘大作业<br />

主要做了微博短文本的情感分析<br />

大作业的结构：<br />

WeiBoSem<br />
	data（处理前和处理后的数据集合）<br />
	model（已经训练好的模型，可以直接调用）<br />
	result_image（我们在训练集合得出的可视化结果）
	w2vForWeiBo（训练词向量和svm模型的训练）<br />
	weibo_web（前端展示页面）<br />
	WordCloud-master（词云生成）<br />
		TestPyxml.py   将xml转成txt<br />
		ChangeToTxt.py  <br />
		NegToTxt.py      负面情感的文本<br />
		NonullTotxt.py	 没有null的文本<br />
		PosTotxt.py		 正面情感的文本<br />
		Feature.py       抽取特征<br />
		ForModel.py		 特征处理（为模型准备）<br />
		NaiveBayes.py	 朴素贝叶斯<br />
		SVM.py		     支撑向量机<br />
		weibospider.py   微博爬虫\n
		基于主题的微博情感分析.docx    大作业文档<br />
		微博情感分析思路.txt           我们的实验思路<br />
	