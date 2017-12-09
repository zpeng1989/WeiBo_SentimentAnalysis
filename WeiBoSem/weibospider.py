# -*- coding: utf-8 -*-

import os
import re
import rsa
import time
import json
import base64
import random
import requests
import binascii
import urllib.parse
from bs4 import BeautifulSoup

class Crawler(object):
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update({
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
			})		

class WeiboCrawler(Crawler):
	def __init__(self, cookies):
		super(WeiboCrawler, self).__init__()
		self.session.cookies = requests.cookies.cookiejar_from_dict(cookies)
		self.ids = set()

	def topic_search(self, topic, topic_id):
		self.topic_get_page(topic, topic_id)

	def topic_load_more(self, soup, topic, topic_id, page, pagebar=0):
		next_mbloglist = soup.find('div', attrs={
				'node-type': 'lazyload'
			})
		time.sleep(random.uniform(2, 5))
		if next_mbloglist is not None:
			action_data = next_mbloglist['action-data']
			self.topic_get_mbloglist(topic, topic_id, page, action_data, pagebar)
		else:
			self.topic_get_page(topic, topic_id, page + 1)

	def parse_page(self, soup, topic):
		count = 0
		for tweet in soup.findAll('div', 'WB_feed_type'):
			data = self.parse_tweet(tweet)
			data['topic'] = topic
			self.save_data(data, topic)
			if data['id'] in self.ids:
				print('[+] get tweet ' + str(data['id']) + ' repeat')
			else:
				print('[+] get tweet ' + str(data['id']))
				self.ids.add(data['id'])
			count += 1
		return count

	def save_data(self, data, topic):
		path = os.path.join('data/weibo', topic)
		if not os.path.isdir(path):
			os.makedirs(path)
		path = os.path.join(path, str(data['id']) + '.json')
		with open(path, 'w+') as f:
			json.dump(data, f, indent=4)

	def parse_tweet(self, tweet):
		author = tweet.find('div', 'WB_info').find('a')
		published = tweet.find('a', attrs={
				'node-type': 'feed_list_item_date'
			})
		content = tweet.find('div', attrs={
				'node-type': 'feed_list_content'
			})
		func_count = tweet.find('div', 'WB_feed_handle')
		if tweet.find('a', 'WB_text_opt'):
			response = self.session.get('https://weibo.com/p/aj/mblog/getlongtext', params={
					'ajwvr': '6',
					'mid': tweet['mid'],
					'__rnd': str(int(time.time()))
				})
			html = response.json()['data']['html']
			content = BeautifulSoup(html, 'lxml')
		return {
			'id': tweet['mid'],
			'author': {
				'id': re.search(r'\bid=(\d+)', author['usercard']).group(1),
				'nickname': author['nick-name']
			},
			'published': {
				'format': published['title'],
				'stamp': published['date']
			},
			'content': {
				'html': content.prettify(),
				'text': self.parse_content(str(content)),
				'topics': self.parse_topic(content),
				'urls': self.parse_urls(content),
				'faces': self.parse_faces(content)
			},
			'forward_count': self.parse_func_count(func_count, 'fl_forward'),
			'comment_count': self.parse_func_count(func_count, 'fl_comment'),
			'like_count': self.parse_func_count(func_count, 'fl_like'),
			'html': tweet.prettify()
		}

	def parse_func_count(self, func_count, action_type):
		try:
			return int(func_count.find('a', attrs={
					'action-type': action_type
				}).findAll('em')[1].string)
		except Exception as e:
			return 0

	def parse_faces(self, content):
		return [{
			'src': i['src'],
			'mean': i['title'][1:-1]
		} for i in content.findAll('img', 'W_img_face')]

	def parse_topic(self, content):
		topics = []
		for topic in content.findAll('a', 'a_topic'):
			topics.append({
				'url': topic['href'],
				'name': re.search('#(.*?)#', topic.string).group(1).strip()
			})
		return topics

	def parse_urls(self, content):
		urls = []
		for url in content.findAll('a', attr={
			'action-type': 'feed_list_url'
		}): 
			url.i.decompose()
			urls.append({
				'link': url['href'],
				'content': url.string
			})
		return urls

	def parse_content(self, content):
		content = re.sub('(<a(| [^<>]*)>[^<>]*)<i(| [^<>]*)>[^<>]*</i>', '\g<1>', content)
		content = re.sub('<img( [^<>]*) class="W_img_face"( [^<>]*) title="([^<>]*)"( [^<>]*|)>', '\g<3>', content)
		content = re.sub('<\/?(p|div|br)(| [^<>]*)>', '\n', content)
		content = re.sub('<[^<>]*>| +', ' ', content)
		return re.sub('\s*\n\s*', '\n', content).strip()

# 默认排序（回复时间排序）
class DefaultSortWeiboCrawler(WeiboCrawler):
	def topic_get_page(self, topic, topic_id, page=1):
		url = 'https://weibo.com/p/%s' % topic_id
		if page >= 23:
			return
		response = self.session.get(url, params={
				'page': str(page)
			})
		with open('test.html', 'wb') as f:
			f.write(response.content)
		soup = BeautifulSoup(response.text, 'lxml')
		scripts = soup.findAll('script')
		for script in scripts:
			match = re.search(r'FM\.view\((\{.*\})\)', script.prettify())
			if match is None:
				continue
			data = json.loads(match.group(1))
			if data.get('domid', '') != 'Pl_Third_App__11':
				continue
			soup = BeautifulSoup(data['html'], 'lxml')
			count = self.parse_page(soup, topic)
			print('[+] count tweets %d from page %d' % (count, page))
			self.topic_load_more(soup, topic, topic_id, page)
			break

	def topic_get_mbloglist(self, topic, topic_id, page, action_data, pagebar):
		url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?' + action_data
		response = self.session.get(url, params={
				'ajwvr': '6',
				'domain': '100808',
				'page': str(page),
				'pagebar': str(pagebar),
				'pl_name': 'Pl_Third_App__11',
				'id': topic_id,
				'script_uri': '/p/' + topic_id,
				'feed_type': '1',
				'pre_page': str(page),
				'domain_op': '100808',
				'__rnd': str(int(time.time()))
			})
		soup = BeautifulSoup(response.json()['data'], 'lxml')
		count = self.parse_page(soup, topic)
		print('[+] count tweets %d from page %d' % (count, page))
		self.topic_load_more(soup, topic, topic_id, page, '1')

# 热门排序
class HotSortWeiboCrawler(WeiboCrawler):
	def topic_get_page(self, topic, topic_id, page=1):
		url = 'https://weibo.com/p/%s' % topic_id
		if page >= 23:
			return
		response = self.session.get(url, params={
				'feed_sort': 'hot',
				'feed_filter': 'hot',
				'page': str(page)
			})
		print(response.url)
		soup = BeautifulSoup(response.text, 'lxml')
		scripts = soup.findAll('script')
		for script in scripts:
			match = re.search(r'FM\.view\((\{.*\})\)', script.prettify())
			if match is None:
				continue
			data = json.loads(match.group(1))
			if data.get('domid', '') != 'Pl_Third_App__11':
				continue
			soup = BeautifulSoup(data['html'], 'lxml')
			count = self.parse_page(soup, topic)
			print('[+] count tweets %d from page %d' % (count, page))
			self.topic_load_more(soup, topic, topic_id, page)
			break

	def topic_get_mbloglist(self, topic, topic_id, page, action_data, pagebar):
		url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?' + action_data
		response = self.session.get(url, params={
				'ajwvr': '6',
				'domain': '100808',
				'page': str(page),
				'pagebar': str(pagebar),
				'pl_name': 'Pl_Third_App__11',
				'id': topic_id,
				'script_uri': '/p/' + topic_id,
				'feed_sort': 'hot',
				'feed_filter': 'hot',
				'pre_page': str(page),
				'domain_op': '100808',
				'__rnd': str(int(time.time())),
				'feed_type': '1'
			})
		print(response.url)
		soup = BeautifulSoup(response.json()['data'], 'lxml')
		count = self.parse_page(soup, topic)
		print('[+] count tweets %d from page %d' % (count, page))
		self.topic_load_more(soup, topic, topic_id, page, '1')

# 发布时间排序
class WhiteSortWeiboCrawler(WeiboCrawler):
	def topic_get_page(self, topic, topic_id, page=1):
		url = 'https://weibo.com/p/%s' % topic_id
		if page >= 23:
			return
		response = self.session.get(url, params={
				'feed_sort': 'white',
				'feed_filter': 'white',
				'page': str(page)
			})
		print(response.url)
		soup = BeautifulSoup(response.text, 'lxml')
		scripts = soup.findAll('script')
		for script in scripts:
			match = re.search(r'FM\.view\((\{.*\})\)', script.prettify())
			if match is None:
				continue
			data = json.loads(match.group(1))
			if data.get('domid', '') != 'Pl_Third_App__11':
				continue
			soup = BeautifulSoup(data['html'], 'lxml')
			count = self.parse_page(soup, topic)
			print('[+] count tweets %d from page %d' % (count, page))
			self.topic_load_more(soup, topic, topic_id, page)
			break

	def topic_get_mbloglist(self, topic, topic_id, page, action_data, pagebar):
		url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?' + action_data
		response = self.session.get(url, params={
				'ajwvr': '6',
				'domain': '100808',
				'page': str(page),
				'pagebar': str(pagebar),
				'pl_name': 'Pl_Third_App__11',
				'id': topic_id,
				'script_uri': '/p/' + topic_id,
				'feed_sort': 'white',
				'feed_filter': 'white',
				'pre_page': str(page),
				'domain_op': '100808',
				'__rnd': str(int(time.time())),
				'feed_type': '1'
			})
		print(response.url)
		soup = BeautifulSoup(response.json()['data'], 'lxml')
		count = self.parse_page(soup, topic)
		print('[+] count tweets %d from page %d' % (count, page))
		self.topic_load_more(soup, topic, topic_id, page, '1')

def crawler_launcher(topic, topic_id, cookies):
	print('[+] 默认排序（回复时间排序）')
	crawler = DefaultSortWeiboCrawler(cookies=cookies)
	crawler.topic_search(topic, topic_id)
	print('[+] 热门排序')
	crawler = HotSortWeiboCrawler(cookies=cookies)
	crawler.topic_search(topic, topic_id)
	print('[+] 发布时间排序')
	crawler = WhiteSortWeiboCrawler(cookies=cookies)
	crawler.topic_search(topic, topic_id)

def main():
	cookies = {
		'SINAGLOBAL': '1453522613679.2456.1500781354384',
		'httpsupgrade_ab': 'SSL',
		'wb_cmtLike_5633457596': '1',
		'un': '13640240375',
		'wvr': '6',
		'YF-Ugrow-G0': '5b31332af1361e117ff29bb32e4d8439',
		'SSOLoginState': '1512776211',
		'SCF': 'AsMB5r8OGSo9x5ahWdNzTy4OhLGYPWzz7Qn7OwNuhrUuaXyqlr3wNjqZqtQqWocW0IsBOTZE-ks8afxSGdIpE6M.',
		'SUB': '_2A253L1JDDeRhGeNI6FEV9SnJwjqIHXVUXcSLrDV8PUNbmtAKLVTykW9NSJSujAwktnIMX3nqjn4u5Jv0CEpSCQt4',
		'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWS45HbUYi0Cs-YLk_p5Fgl5JpX5KMhUgL.Fo-ce0eXSKMf1Kq2dJLoIE.LxKqLBKzLBKqLxK-LBo.LB.zLxK-LBKBLBKMLxKBLB.BLB.qNeK50SBtt',
		'SUHB': '0Yhh0_-L8t-4va',
		'ALF': '1544312210',
		'YF-V5-G0': 'a53c7b4a43414d07adb73f0238a7972e',
		'wb_cusLike_5633457596': 'N',
		'YF-Page-G0': 'f70469e0b5607cacf38b47457e34254f',
		'_s_tentry': 'login.sina.com.cn',
		'UOR': 'www.anjian.com,widget.weibo.com,login.sina.com.cn',
		'Apache': '7791072881731.7705.1512776213966',
		'ULV': '1512776214022:25:3:2:7791072881731.7705.1512776213966:1512734311205',
		'TC-V5-G0': '06f20d05fbf5170830ff70a1e1f1bcae',
		'TC-Page-G0': '2b304d86df6cbca200a4b69b18c732c4'
	}
	topics = [{
		'name': '运动教室',
		'id': '100808afb98cdb69e23308b06196b0b0d3f132'
	}, {
		'name': '易烊千玺2017巅峰人物新生耀目',
		'id': '1008081419755210db047627a1190a92deb07a'
	}, {
		'name': '梦想的声音',
		'id': '1008082e54ce464bc8a6c830337898dcd0d096'
	}, {
		'name': '亚洲新歌榜',
		'id': '1008085d82c934b97e5cef62b0ed6ab7adc813'
	}, {
		'name': '30天安利张杰',
		'id': '1008088d1fe6448c432adfd6e48e8bc730b7cb'
	}, {
		'name': '你好旧时光',
		'id': '1008086493e069bf491dcd1a7bfe82339f936d'
	}, {
		'name': '鹿晗愿望季',
		'id': '10080812a77be060c9b1e5a95bd8b656ca3fec'
	}, {
		'name': '李宇春流行',
		'id': '100808c04b99d36aa2c478604cce9cc4c35423'
	}]
	for topic in topics:
		crawler_launcher(topic['name'], topic['id'], cookies)

if __name__ == '__main__':
	main()


# session.cookies = requests.cookies.cookiejar_from_dict({
		
# 	})

# response = session.get('https://weibo.com', verify=False)

# with open('test.html', 'wb+') as f:
# 	f.write(response.content)

# username = '377016661@qq.com'
# password = 'Maiyifeng123'

# username = urllib.parse.quote_plus(username)
# username = base64.b64encode(username.encode('utf-8'))

# url = 'https://login.sina.com.cn/sso/prelogin.php'
# response = session.get(url, params={
# 		'entry': 'weibo',
# 		'callback': '',
# 		'su': username,
# 		'rsakt': 'mod',
# 		'checkpin': '1',
# 		'client': 'ssologin.js(v1.4.19)',
# 		'_': '1511915845486'
# 	}, headers={
# 		'User-Agent': ''
# 	}, verify=False)
# data = response.json()
# print(json.dumps(data, indent=4))
# data['servertime'] = '1511922880'
# data['nonce'] = 'BR9PU8'

# pub_key = int(data['pubkey'], 16)
# key = rsa.PublicKey(pub_key, 65537)
# message = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(password)
# password = binascii.b2a_hex(rsa.encrypt(message.encode('utf-8'), key))

# url = 'https://login.sina.com.cn/sso/login.php'
# response = session.post(url, data={
# 		'entry': 'weibo',
# 		'gateway': '1',
# 		'from': '',
# 		'savestate': '7',
# 		'qrcode_flag': 'false',
# 		'useticket': 1,
# 		'vsnf': 1,
# 		'su': username,
# 		'service': 'miniblog',
# 		'servertime': int(time.time()),
# 		'nonce': str(data['nonce']),
# 		'pwencode': 'rsa2',
# 		'rsakv': str(data['rsakv']),
# 		'sp': password,
# 		'sr': '1536*864',
# 		'encoding': 'UTF-8',
# 		'cdult': '2',
# 		'domain': 'weibo.com',
# 		'prelt': '43',
# 		'returnType': 'TEXT',
# 		'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F'
# 	}, verify=False, params={
# 		'client': 'ssologin.js(v1.4.19)'
# 	})

# response.encoding = 'gb2312'
# print(response.text)

# url = 'http://weibo.com'

# response = session.get(url, verify=False)
# response.encoding = 'gb2312'
# with open('test.html', 'wb+') as f:
# 	f.write(response.content)

# print(response.text)




# TED字幕数据统计

# import os

# if os.path.isfile('statistics_ted_20171121.json'):
# 	with open('statistics_ted_20171121.json') as f:
# 		statistics = json.load(f)
# else:
# 	statistics = 


'''
# 千岛日报数据统计

import re
import os
import json

if os.path.isfile('test.json'):
	with open('test1.json') as f:
		statistics = json.load(f)
else:
	statistics = {}

paths = [
	'D:/project/crawler/data/qiandaoribao',
	'D:/project/crawler/data/_qiandaoribao',
	'D:/project/DMC/qiandaoribao'
]

for path in paths:
	for filename in os.listdir(path):
		_path = os.path.join(path, filename)
		with open(_path) as f:
			data = json.load(f)
		# 挑选译文篇章
		if not re.search(r'译文', data['body']):
			continue
		month = data['pub_time'][:7]
		if month not in statistics.keys():
			statistics[month] = []
		if data['request_url'] not in statistics[month]:
			statistics[month].append(data['request_url'])

with open('test1.json', 'w+') as f:
	json.dump(statistics, f, indent=4)

for key, value in statistics.items():
	statistics[key] = len(value)

print(json.dumps(statistics, indent=4))

'''

# pub_time
# request_url



# import requests
# from requests.adapters import HTTPAdapter
# from requests.cookies import cookiejar_from_dict

# class Request:
# 	def __init__(self):
# 		self.session = requests.Session()
# 		self.headers.update({
# 			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
# 			})
# 		self.session.mount('http://', HTTPAdapter(max_retries=5))
# 		self.session.mount('https://', HTTPAdapter(max_retries=5))

# 	def __getattr__(self, key):
# 		return getattr(self.session, key)

# 	def set_cookies(self, cookie_for_str=None, cookie_for_dist=None):
# 		if cookie_for_str is not None:
# 			cookie = {}
# 			for row in cookie_for_str.split(';'):
# 				if row.strip() == '':
# 					continue
# 				key, value = row.split('=')
# 				cookie[key.strip()] = value.strip()
# 			return set_cookies(cookie_for_dist=cookie)
# 		elif cookie_for_dist is not None:
# 			self.session.cookie = cookiejar_from_dict(cookiejar_from_dict)

# 	def get(self, url, *args, **kwargs):
# 		response = self.session.get(url, *args, **kwargs)
# 		self.headers.update({
# 				'Referer': response.url
# 			})
# 		return response

# 	def post(self, url, *args, **kwargs):
# 		response = self.session.post(url, *args, **kwargs)
# 		self.headers.update({
# 				'Referer': response.url
# 			})
# 		return response

# session = Request()

# session.get('https://www.baidu.com')
# session.get('https://www.baidu.com')
# print(session.headers)

# import re
# import os
# import json
# from datetime import date
# from html.parser import HTMLParser
# from urllib.parse import urljoin
# from bs4 import BeautifulSoup
# from pyquery import PyQuery

# def parseHTML(html):
# 	html = re.sub(r'<!--[\w\W]*?-->|<script([^<>]*)>[\w\W]*?</script>', '', html)
# 	html = re.sub(r'<\/?(p|div|pre|li|ul|br)( [^<>]*?)?>', '\n', html)
# 	html = re.sub(r'<[^<>]*?>', '', html)
# 	html = re.sub(r'\s*\n\s*', '\n', html)
# 	html = re.sub(r'[^\S\n]+', ' ', html).strip()
# 	return HTMLParser().unescape(html)

# def main():
# 	path = 'data/wechat'
# 	nonce = set()
# 	count = 0
# 	for index, filename in enumerate(os.listdir(path)):
# 		filepath = '%s/%s' % (path, filename)
# 		with open(filepath, encoding='utf-8') as f:
# 			html = f.read()
# 		_html = PyQuery(html)
# 		content = _html('#js_content').html()
# 		content = parseHTML(content)
# 		title = _html('h2#activity-name').text()
# 		_id = _html('script:first-child').attr('nonce')
# 		gongzhonghao = re.search('var nickname = "(.*?)"', html).group(1)
# 		pub_time = re.search('var publish_time = "(.*?)"', html).group(1)
# 		with open('data/wechat_parse/%s.json' % _id, 'w+') as f:
# 			json.dump({
# 				'id': _id,
# 				'title': title,
# 				'content': content,
# 				'author': gongzhonghao,
# 				'pub_time': pub_time
# 			}, f, indent=4)

# if __name__ == '__main__':
# 	main()

# def loadData():
# 	for keyword in os.listdir('data'):
# 		path = 'data/%s' % keyword
# 		for filename in os.listdir(path):
# 			file = 'data/%s/%s' % (keyword, filename)
# 			with open(file) as f:
# 				yield json.load(f), file



# def parseData(data):
# 	data['title'] = parseHTML(data['title'])	
# 	data['content'] = parseHTML(data['content'])
# 	if data['type'] == 'question':
# 		data['created_time'] = str(date.fromtimestamp(data['created_time']))
# 		data['updated_time'] = str(date.fromtimestamp(data['updated_time']))
# 		for answer in data['answers']:
# 			answer['content'] = parseHTML(answer['content'])
# 			answer['created_time'] = str(date.fromtimestamp(answer['created_time']))
# 			answer['updated_time'] = str(date.fromtimestamp(answer['updated_time']))
# 			for comment in answer['comments']:
# 				comment['content'] = parseHTML(comment['content'])
# 				comment['created_time'] = str(date.fromtimestamp(comment['created_time']))
# 				if comment['is_reply_to_author']:
# 					comment['reply_to_author'] = {
# 						'id': comment['reply_to_author']['member']['id'],
# 						'name': comment['reply_to_author']['member']['name'],
# 						'url_token': comment['reply_to_author']['member']['url_token']
# 					}
# 	elif data['type'] == 'zhuanlan':
# 		data['published_time'] = data['published_time'][:10]
# 		for comment in data['comments']:
# 			comment['url'] = urljoin('https://zhuanlan.zhihu.com', comment['url'])
# 			comment['created_time'] = comment['created_time'][:10]
# 			comment['content'] = parseHTML(comment['content'])

# 	return data

# def saveParseData(data, path):
# 	path = 'sub' + path
# 	dirpath = os.path.dirname(path)
# 	if not os.path.isdir(dirpath):
# 		os.makedirs(dirpath)
# 	with open(path, 'w+') as f:
# 		json.dump(data, f, indent=4)

# def main():
# 	for data, path in loadData():
# 		data = parseData(data)
# 		saveParseData(data, path)

# if __name__ == '__main__':
# 	main()
