# -*- coding: utf-8 -*-
import StringIO
import binascii
import random
import socket
import struct
import string

class PKCS7Encoder(object):
	def __init__(self, k=16):
	   self.k = k

	def decode(self, text):
		nl = len(text)
		val = int(binascii.hexlify(text[-1]), 16)
		if val > self.k:
			raise ValueError('Input is not padded or padding is corrupt')
		l = nl - val
		return text[:l]

	def encode(self, text):
		l = len(text)
		output = StringIO.StringIO()
		val = self.k - (l % self.k)
		for _ in xrange(val):
			output.write('%02x' % val)
		return text + binascii.unhexlify(output.getvalue())

class Tools(object):
	def __init__(self):
		pass
		
	def genRandomIP(self):
		return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

	def rndHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])

	def rndNum(self,n):
		return ''.join([random.choice('0123456789') for x in range(random.randint(n-1,n))])

	def rndAlp(self,n):
		return ''.join([random.choice(string.ascii_lowercase) for x in range(random.randint(n-1,n))])

	def rndUser(self):
		return '%s%s'%(self.rndAlp(7),self.rndNum(4))

	def rndPw(self,n):
		return ''.join([random.choice(string.ascii_letters + string.digits) for x in range(n)])#+ string.punctuation

	def rndDeviceId(self):
		s='%s-%s-%s-%s-%s'%(self.rndHex(8),self.rndHex(4),self.rndHex(4),self.rndHex(4),self.rndHex(12))
		return s