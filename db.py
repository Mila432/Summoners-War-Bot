# -*- coding: utf-8 -*-
import sqlite3
import os.path

class Database(object):
	def __init__(self):
		self.sqlite_file='accounts.db'
		if not os.path.isfile(self.sqlite_file):
			self.createDb()

	def createDb(self):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute('''CREATE TABLE "data" ("id" INTEGER UNIQUE,"energy" INTEGER,"mana" INTEGER,"crystal" INTEGER,"level" INTEGER,"uid" INTEGER,"did" INTEGER,PRIMARY KEY("id"));''')
		conn.commit()
		conn.close()

	def addAccount(self,id,energy,mana,crystal,level,uid,did):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("INSERT OR IGNORE INTO data (id,energy,mana,crystal,level,uid,did) VALUES (%s,%s,%s,%s,%s,%s,%s)"%(id,energy,mana,crystal,level,uid,did))
		conn.commit()
		conn.close()

	def updateAccount(self,level,gold,rmb,app_uid):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("UPDATE data SET level=%s,gold=%s,rmb=%s where app_uid='%s'"%(int(level),int(gold),int(rmb),app_uid))
		conn.commit()
		conn.close()

	def getAccount(self):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		c.execute("select uid,did from data")
		all_rows = c.fetchall()
		res=[]
		for x in all_rows:
			res.append('%s;%s'%x)
		conn.close()
		return res

	def getAllAccounts(self,limit=None):
		conn = sqlite3.connect(self.sqlite_file)
		c = conn.cursor()
		if limit:
			c.execute("select app_token,app_uid from data where rmb>%s"%(limit))
		else:
			c.execute("select app_token,app_uid from data")
		all_rows = c.fetchall()
		conn.close()
		return all_rows

if __name__ == '__main__':
	db=Database()
	db.createDb()