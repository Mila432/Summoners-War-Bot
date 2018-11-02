from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.PublicKey import RSA
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
import re
import requests
import socket
import sys
import time
import zlib
from crypt import Crypter

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
		self.s.headers.update({'User-Agent':'Summoners%20War/4.1.2.41200 CFNetwork/808.2.16 Darwin/16.3.0','Accept-Language':'en-gb'})
		self.did=did
		self.guest_uid=None
		self.p1='{"hive_country":"%s","device_country":"RU","analytics_id":"","timezone":null,"language":"en","game_language":"en","server_id":""}'
		self.p2='{"hive_country":"%s","device_country":"RU","analytics_id":"","guest_uid":"%s","timezone":null,"language":"en","game_language":"en","server_id":""}'
		if True:
			self.appid='com.com2us.smon.normal.freefull.apple.kr.ios.universal'#IOS
		else:
			self.appid='com.com2us.smon.normal.freefull.google.kr.android.common'#ANDROID
		self._crypter=Crypter()
		self.getCountry()
		
	def MD5(self,i):
		m = hashlib.md5()
		m.update(i)
		return m.hexdigest()
		
	def getCountry(self):
		r=self.s.get('http://summonerswar-eu.com2us.net/api/location_c2.php')
		self.hive_country=json.loads(self._crypter.decrypt_response(r.content,2))['country_code']
		return self.hive_country

	def create(self):
		res = json.loads(self.s.post('https://api.qpyou.cn/guest/create',data=self.p1%(self.hive_country)).content)
		if res['error_code']==1401:
			print 'ip banned'
			if socket.gethostname()=='Admin-PC':
				return self.create()
			exit(1)
		self.guest_uid=res['guest_uid']
		return res

	def key(self):
		return json.loads(self.s.post('https://api.qpyou.cn/guest/key',data='{"hive_country":"RU","device_country":"RU","analytics_id":"","timezone":null,"language":"en","game_language":"en","server_id":""}').content)

	def generate(self,public_key,signature):
		cipher = Cipher_PKCS1_v1_5.new(RSA.importKey(public_key.rstrip()))
		emsg='{"did":"%s","appid":"%s","expire_time":"%s","hive_country":"%s","signature":"%s"}'%(self.did,self.appid,str(time.time()+300),self.hive_country,signature) #thanks https://github.com/aceradryd for hint
		b64data=base64.b64encode(cipher.encrypt(emsg.encode()))
		return json.loads(self.s.post('https://api.qpyou.cn/guest/generate',data=b64data).content)

	def auth(self,guest_uid):
		return json.loads(self.s.post('https://api.qpyou.cn/guest/auth',data=self.p2%(self.hive_country,guest_uid)).content)

	def registered(self):
		return json.loads(self.s.post('https://api.qpyou.cn/device/registered',data=self.p1%(self.hive_country)).content)
		
	def me(self):
		res=self.s2.post('https://api.qpyou.cn/user/me',data=self.p1%(self.hive_country),headers={'Content-Type':'application/json','Accept-Language':'en-gb','User-Agent':'Summoners%20War/3.8.6.38601 CFNetwork/808.2.16 Darwin/16.3.0'})
		if 'thorization Faile' in res.content:
			return None
		return json.loads(res.content)

	def otpVerification(self,udata):
		if 'ct' not in udata and 'iv' not in udata and '"s"' not in udata and '"d"' not in udata:
			print 'bad data'
			exit(1)
		r=self.s2.post('https://hub.qpyou.cn/otp/verification',data=udata,headers={'Accept':'application/json, text/javascript, */*; q=0.01','Origin':'https://hub.qpyou.cn','X-Requested-With':'XMLHttpRequest','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','DNT':'1','Referer':'https://hub.qpyou.cn/otp/main'})
		return json.loads(r.content)['result']==0

	def hiveLogin(self,user,password):
		self.s2=requests.Session()
		self.s2.verify=False
		self.s2.headers.update({'Upgrade-Insecure-Requests':'1','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1'})
		if 'Admin-PC' == socket.gethostname():
			self.s2.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})
		#self.registered()
		s2r=self.s2.get('https://hub.qpyou.cn/auth')
		if '/hub.qpyou.cn/auth/login_proc' not in s2r.content:
			print 'login page broken'
			exit(1)
		rr= self.s2.post('https://hub.qpyou.cn/auth/login_proc',data='id={}&password=&dkagh={}'.format(user,self.MD5(password)),headers={'Cache-Control':'max-age=0','Origin':'https://hub.qpyou.cn','Upgrade-Insecure-Requests':'1','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1','Referer':'https://hub.qpyou.cn/auth/login'})
		if '/otp/main' in rr.url:
			print 'detected otp..'
			if 'class="join_otp"' in rr.content:
				_send_to=re.search('class="user_inform">(.*)</span>',rr.content).group(1)
				_udata=raw_input('Open this: /otp/aes.html?mail=%s&code=123456 and paste the console log here:\n'%(_send_to))
				if self.otpVerification(_udata.rstrip()):
					rr=self.s2.get('https://hub.qpyou.cn/otp/login',headers={'Cache-Control':'max-age=0','Origin':'https://hub.qpyou.cn','Upgrade-Insecure-Requests':'1','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1','Referer':'https://hub.qpyou.cn/otp/main'})
					if '/gdpr/login' in rr.url:
						rr=self.s2.post('https://hub.qpyou.cn/userinfo/gdpr/done',data='',headers={'Cache-Control':'max-age=0','Origin':'https://hub.qpyou.cn','Upgrade-Insecure-Requests':'1','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1','Referer':'https://hub.qpyou.cn/userinfo/gdpr/login'},allow_redirects=False)
		self.s2.cookies.update({'gameindex':'2623','hive_config_language':'en_US','inquiry_language':'en_US','advertising_id':'00000000-0000-0000-0000-000000000000','appid':'com.com2us.smon.normal.freefull.apple.kr.ios.universal','device':'iPad5,4','did':str(random.randint(200000000,300000000)) if not self.did else str(self.did),'native_version':'Hub v.2.6.5','osversion':'10.2','platform':'ios','vendor_id':Tools().rndDeviceId()})
		rr= self.s2.post('https://hub.qpyou.cn/auth/login_proc',data='id={}&password=&dkagh={}'.format(user,self.MD5(password)),headers={'Cache-Control':'max-age=0','Origin':'https://hub.qpyou.cn','Upgrade-Insecure-Requests':'1','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1','Referer':'https://hub.qpyou.cn/auth/login'},allow_redirects=False)
		_uid=None
		if '/gdpr/login' in rr.headers['Location']:
			rr=self.s2.post('https://hub.qpyou.cn/userinfo/gdpr/done',data='',headers={'Cache-Control':'max-age=0','Origin':'https://hub.qpyou.cn','Upgrade-Insecure-Requests':'1','Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','DNT':'1','Referer':'https://hub.qpyou.cn/userinfo/gdpr/login'},allow_redirects=False)
		if 'c2shub://login?error_code' in rr.headers['Location']:
			sss= rr.headers['Location'].split('&')
			_uid = sss[1].replace('uid=','')
			sessionkey=sss[3].replace('sessionkey=','')
			_did = sss[2].replace('did=','')

		if not _uid:
			return None
		return _uid,_did,sessionkey

	def createNew(self):
		self.s.cookies.update({'advertising_id':Tools().rndDeviceId(),'appid':'com.com2us.smon.normal.freefull.apple.kr.ios.universal','device':'iPad5,4','did':str(random.randint(200000000,300000000)) if not self.did else str(self.did),'native_version':'Hub v.2.6.4','osversion':'10.2','platform':'ios','vendor_id':Tools().rndDeviceId()})
		self.registered()
		res=self.key()
		public_key=res['public_key']
		signature=res['signature']
		res=self.generate(public_key,signature)
		self.auth(res['guest_uid'])
		return res['guest_uid'],res['did']
