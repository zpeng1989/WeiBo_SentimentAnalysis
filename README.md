# WeiBo_SentimentAnalysis


数据挖掘大作业

主要做了微博短文本的情感分析

大作业的结构：

WeiBoSem
	data（处理前和处理后的数据集合）\n
	model（已经训练好的模型，可以直接调用）\n
	result_image（我们在训练集合得出的可视化结果）
	w2vForWeiBo（训练词向量和svm模型的训练）\n
	weibo_web（前端展示页面）\n
	WordCloud-master（词云生成）\n
		TestPyxml.py   将xml转成txt\n
		ChangeToTxt.py  \n
		NegToTxt.py      负面情感的文本\n
		NonullTotxt.py	 没有null的文本\n
		PosTotxt.py		 正面情感的文本\n
		Feature.py       抽取特征\n
		ForModel.py		 特征处理（为模型准备）\n
		NaiveBayes.py	 朴素贝叶斯\n
		SVM.py		     支撑向量机\n
		weibospider.py   微博爬虫\n
		基于主题的微博情感分析.docx    大作业文档\n
		微博情感分析思路.txt           我们的实验思路\n
		
	