from Crypto.Cipher import AES
from hashlib import md5
from tools import Tools,PKCS7Encoder
import StringIO
import base64
import binascii
import hashlib
import io
import json
import os
import random
import requests
import socket
import sys
import time
import zlib

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Activeuser(object):
	def __init__(self):
		self.encoder = PKCS7Encoder()
		self.mode = AES.MODE_CBC
		self.s=requests.session()
		self.s.verify=False
		self.s.headers.update({'Content-Type':'text/html','Accept-Language':'en-gb','User-Agent':'SMON_Kr/3.7.8.37800 CFNetwork/808.2.16 Darwin/16.3.0'})

	def getTS(self):
		return str(int(time.time()))

	def callAPI(self,data):
		ts=self.getTS()
		key=self.getkey(ts)
		new_data=self.encrypt(data,key)
		r=self.s.post('https://activeuser.qpyou.cn/gateway.php',data=new_data,headers={'REQ-TIMESTAMP':ts,'REQ-AUTHKEY':self.makeAUTHKEY('%s:%s'%(new_data,ts))})
		return self.decode('%s:%s'%(r.content,r.headers['REQ-TIMESTAMP']))

	def makeAUTHKEY(self,s):
		return self.getmd5(self.decode(s))

	def decode(self,s):
		encoded_data,ts=s.split(':')
		key=self.getkey(ts)
		return self.decrypt(encoded_data,key)

	def decrypt(self,s,key):
		e = AES.new(key, self.mode,'\x00'*16)
		return self.encoder.decode(e.decrypt(base64.b64decode(s)))

	def encrypt(self,s,key):
		e = AES.new(key, self.mode,'\x00'*16)
		return base64.b64encode(e.encrypt(self.encoder.encode(s)))

	def getkey(self,s):
		return self.getmd5(s)[:16]

	def getmd5(self,s):
		return md5(s).hexdigest()

class QPYOU(object):
	def __init__(self,did=None):
		self.s=requests.Session()
		self.s.verify=False
		if 'Admin-PC' == socket.gethostname():
			self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})
		self.s.headers.update({'Content-Type':'application/json','Accept-Language':'en-gb','User-Agent':'SMON_Kr/3.7.0.37000 CFNetwork/808.2.16 Darwin/16.3.0'})
		self.did=did
		self.guest_uid=None
		self.p1='{"language":"en","timezone":null,"game_language":"en","server_id":"","device_country":"RU","hive_country":"RU"}'
		self.p2='{"hive_country":"RU","device_country":"RU","guest_uid":"%s","timezone":null,"language":"en","game_language":"en","server_id":""}'
		
	def MD5(self,i):
		m = hashlib.md5()
		m.update(i)
		return m.hexdigest()
		
	def create(self):
		res = json.loads(self.s.post('https://api.qpyou.cn/guest/create',data=self.p1).content)
		if res['error_code']==1401:
			print 'ip banned'
			if socket.gethostname()=='Admin-PC':
				return self.create()
			exit(1)
		self.guest_uid=res['guest_uid']
		return res
	
	def auth(self):
		return json.loads(self.s.post('https://api.qpyou.cn/guest/auth',data=self.p2%(self.guest_uid)).content)
		
	def registered(self):
		return json.loads(self.s.post('https://api.qpyou.cn/device/registered',data=self.p1).content)
		
	def me(self):
		res=self.s.post('https://api.qpyou.cn/user/me',data=self.p1)
		if 'thorization Faile' in res.content:
			return None
		return json.loads(res.content)

	def hiveLogin(self,user,password):
		self.s.cookies.update({'hive_config_language':'en_US','hive_config_nationality':'CH','inquiry_language':'en_US','advertising_id':'00000000-0000-0000-0000-000000000000','appid':'com.com2us.smon.normal.freefull.apple.kr.ios.universal','device':'iPad5,4','did':str(random.randint(200000000,300000000)) if not self.did else str(self.did),'native_version':'Hub v.2.6.5','osversion':'10.2','platform':'ios','vendor_id':Tools().rndDeviceId(),'gameindex':'2623','hive_source':'C'})
		self.registered()
		r1=self.s.post('https://hub.qpyou.cn/auth',data='{"language":"en","timezone":null,"game_language":"en","server_id":"","device_country":"RU","hive_country":"CH"}',allow_redirects=False)
		data='id={}&password=&dkagh={}'.format(user,self.MD5(password))
		self.s.get('https://hub.qpyou.cn/auth/recent_account',cookies=r1.cookies)
		rr= self.s.post('https://hub.qpyou.cn/auth/login_proc',data=data,headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0 Mobile/14C92 Safari/602.1','Referer':'http://hub.qpyou.cn/auth/login'},allow_redirects=False)
		if '/otp/' in rr.headers['Location']:
			print 'detected otp..'
			self.s.get('https://hub.qpyou.cn/otp/main',headers={'Origin':'https://hub.qpyou.cn','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','User-Agent':'Mozilla/5.0 (iPad; CPU OS 10_2 like Mac OS X) AppleWebKit/602.3.12 (KHTML, like Gecko) Mobile/14C92','Accept-Language':'en-gb','Referer':'https://hub.qpyou.cn/auth/recent_account'})
			_udata=raw_input('Open this: /otp/aes.html?mail=MYMAIL@MY.COM&code=123456 and paste the console log here')
			if 'ct' not in _udata and 'iv' not in _udata and '"s"' not in _udata and '"d"' not in _udata:
				print 'bad data'
				exit(1)
			self.s.post('https://hub.qpyou.cn/otp/verification',data=_udata)
			rr=self.s.get('https://hub.qpyou.cn/otp/login')
		sss= rr.headers['Location'].split('&')
		sessionkey=sss[3].replace('sessionkey=','')
		_did=sss[2].replace('did=','')
		res=self.me()
		if not res:
			return None
		return res['uid'],_did,sessionkey

	def createNew(self):
		self.s.cookies.update({'advertising_id':Tools().rndDeviceId(),'appid':'com.com2us.smon.normal.freefull.apple.kr.ios.universal','device':'iPad5,4','did':str(random.randint(200000000,300000000)) if not self.did else str(self.did),'native_version':'Hub v.2.6.4','osversion':'10.2','platform':'ios','vendor_id':Tools().rndDeviceId()})
		self.registered()
		res=self.create()
		self.auth()
		return res['guest_uid'],res['did']