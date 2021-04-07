# -*- coding: utf-8 -*-
from collections import OrderedDict
from crypt import Crypter
from qpyou import QPYOU
from random import randint
from tools import Tools
import json
import random
import requests
import socket
import sys
import threading
import time
import io
import traceback
from db import Database

import unitinfo
import text_eng

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self,uid,did,user=None,password=None):
		self.crypter=Crypter()
		self.s=requests.session()
		self.s.verify=False
		self.s.timeout=4
		self.s.headers.update({'User-Agent':'Summoners%20War/5.3.8.53800 CFNetwork/1121.2.2 Darwin/19.3.0'})
		#if 'Admin-PC' == socket.gethostname():
		#self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'http://127.0.0.1:8888',})
		self.game_index=2623
		self.proto_ver=11851
		self.sec_ver='B1aq0bPv'
		self.app_version='6.2.3'
		self.c2_api='https://summonerswar-%s.qpyou.cn/api/gateway_c2.php'
		if uid:	self.uid=int(uid)
		if did:	self.did=int(did)
		self.isHive=user is not None
		self.infocsv=''
		if user and password:
			self.log('hive account')
			q=QPYOU()
			#q.setProxy('127.0.0.1:8888')
			q.getdid()
			q.hiveLogin(user,password)
			self.did=q.did
			self.uid=q.uid
			self.session_key=q.sessionkey
			self._id=user
			self.email=q.mev2()['email']
		self.log('uid:%s did:%s'%(self.uid,self.did))
		self.db=Database()

	def setProxy(self,prox):
		self.s.proxies.update({'http': 'http://%s'%prox,'https': 'http://%s'%prox,})

	def save(self,data,file):
		with io.open(file, 'a', encoding='utf8') as thefile:
			thefile.write('%s\n'%unicode(data))

	def setIsBadBot(self):
		self.IsBadBot=True

	def setCanRefill(self):
		self.refillEnergy=True

	def setCanArena(self):
		self.canArena=True

	def setRegion(self,region=None):
		regions=['gb','hub','jp','cn','sea','eu']
		'''
		gb = global
		eu = europe
		jp = japan
		sea = asia
		cn = china
		hub = korea
		'''
		if region not in regions:
			self.log('invalid region, choose one from these:%s'%(','.join(regions)))
			#exit(1)
			region=random.choice(regions)
		if region=='eu':	region='eu-lb'
		self.region=region
		self.c2_api=self.c2_api%(self.region)

	def setIDFA(self,id):
		self.idfa=id

	def log(self,msg):
		try:
			print '[%s] %s'%(time.strftime('%H:%M:%S'),msg.encode('utf-8'))
		except:
			pass

	def getText(self,j,i):
		return text_eng.data[str(j)][str(i)]

	def getUnit(self,i):
		return unitinfo.data[str(i)]

	def callAPI(self,path,data,repeat=False):
		#try:
			old_data=None
			if not repeat:
				if type(data)<>str:
					old_data=data
					data=json.dumps(data, indent=1).replace(' ','	').replace(',	',',')
				data=self.crypter.encrypt_request(data,2 if '_c2.php' in path else 1)
			ts=int(time.time())
			#try:
			if True:
				res=self.s.post(path,data,headers={'SmonTmVal':str(old_data['ts_val']) if 'ts_val' in old_data else str(self.crypter.GetPlayerServerConnectElapsedTime(ts)),'SmonChecker':self.crypter.getSmonChecker(data,ts)})
			#except KeyboardInterrupt:
			#	return None
			#except:
			#	return self.callAPI(path,data,True)
			res= self.crypter.decrypt_response(res.content,2 if '_c2.php' in path else 1)
			rj=json.loads(res)
			if 'block_info' in rj:
				self.log('banned')
				exit(1)
			if 'wizard_info' in res and 'wizard_id' in res:
				self.updateWizard(rj['wizard_info'])
				self.setUser(rj)
			if 'session_key' in rj:	self.session_key=rj['session_key']
			#print rj
			if 'ret_code' in res:
				if rj['ret_code']<>0:
					self.log('failed to send data for %s'%(rj['command']))
					return None
				#self.log('ret_code:%s command:%s'%(rj['ret_code'],rj['command']))
			return rj
		#except KeyboardInterrupt:
		#	return None
		#except:
		#	return self.callAPI(path,data,True)

	def getServerStatus(self):
		data={}
		data['game_index']=self.game_index
		data['proto_ver']=self.proto_ver
		data['sec_ver']=self.sec_ver
		data['channel_uid']=0
		return self.callAPI('https://summonerswar-eu.qpyou.cn/api/server_status_c2.php',data)

	def getVersionInfo(self):
		data={}
		data['game_index']=self.game_index
		data['proto_ver']=self.proto_ver
		data['sec_ver']=self.sec_ver
		data['channel_uid']=0
		res= self.callAPI('https://summonerswar-eu.qpyou.cn/api/version_info_c2.php',data)
		self.parseVersionData(res['version_data'])
		return res

	def parseVersionData(self,input):
		for v in input:
			if v['topic']=='protocol':
				self.log('found proto_ver:%s'%(v['version']))
				self.proto_ver=int(v['version'])
			if v['topic']=='infocsv':
				self.log('found infocsv:%s'%(v['version']))
				self.infocsv=v['version']

	def base_data(self,cmd,kind=1):
		if kind == 1:
			data=OrderedDict([('command',cmd),('game_index',self.game_index),('session_key',self.getUID()),('proto_ver',self.proto_ver),('sec_ver',self.sec_ver),('infocsv',self.infocsv),('channel_uid',self.uid)])
		elif kind ==2:
			data=OrderedDict([('command',cmd),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime())])
		return data

	def CheckLoginBlock(self):
		data=self.base_data('CheckLoginBlock')
		return self.callAPI(self.c2_api,data)

	def GetDailyQuests(self):
		data=self.base_data('GetDailyQuests',2)
		return self.callAPI(self.c2_api,data)

	def GetMiscReward(self):
		data=self.base_data('GetMiscReward',2)
		return self.callAPI(self.c2_api,data)

	def GetMailList(self):
		data=self.base_data('GetMailList',2)
		return self.callAPI(self.c2_api,data)

	def GetRtpvpQuests(self):
		data=self.base_data('GetRtpvpQuests',2)
		return self.callAPI(self.c2_api,data)

	def ExpandUnitSlot(self):
		data=OrderedDict([('command','ExpandUnitSlot'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('cash_used',0)])
		return self.callAPI(self.c2_api,data)

	def BuyIsland(self,island_id=2):
		data=OrderedDict([('command','BuyIsland'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('island_id',island_id)])
		return self.callAPI(self.c2_api,data)

	def WriteClientLog(self,logdata={}):
		data=OrderedDict([('command','WriteClientLog'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('logdata',logdata)])
		return self.callAPI(self.c2_api,data)

	def GetContentsUpdateNotice(self):
		data=OrderedDict([('command','GetContentsUpdateNotice'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('app_version',self.app_version),('lang','en')])
		return self.callAPI(self.c2_api,data)

	def GetArenaLog(self):
		data=self.base_data('GetArenaLog',2)
		return self.callAPI(self.c2_api,data)

	def getUnitStorageList(self):
		data=self.base_data('getUnitStorageList',2)
		return self.callAPI(self.c2_api,data)

	def getUpdatedDataBeforeWebEvent(self):
		data=self.base_data('getUpdatedDataBeforeWebEvent',2)
		return self.callAPI(self.c2_api,data)

	def ReceiveDailyRewardSpecial(self):
		data=self.base_data('ReceiveDailyRewardSpecial',2)
		return self.callAPI(self.c2_api,data)

	def receiveDailyRewardInactive(self):
		data=self.base_data('receiveDailyRewardInactive',2)
		return self.callAPI(self.c2_api,data)

	def GetRTPvPInfo_v3(self):
		data=self.base_data('GetRTPvPInfo_v3',2)
		return self.callAPI(self.c2_api,data)

	def getUnitUpgradeRewardInfo(self):
		data=self.base_data('getUnitUpgradeRewardInfo',2)
		return self.callAPI(self.c2_api,data)

	def GetCostumeCollectionList(self):
		data=self.base_data('GetCostumeCollectionList',2)
		return self.callAPI(self.c2_api,data)

	def CheckDarkPortalStatus(self):
		data=self.base_data('CheckDarkPortalStatus',2)
		return self.callAPI(self.c2_api,data)

	def GetFriendRequest(self):
		data=self.base_data('GetFriendRequest',2)
		return self.callAPI(self.c2_api,data)

	def GetChatServerInfo(self):
		data=self.base_data('GetChatServerInfo',2)
		return self.callAPI(self.c2_api,data)

	def getRtpvpRejoinInfo(self):
		data=self.base_data('getRtpvpRejoinInfo',2)
		return self.callAPI(self.c2_api,data)

	def GetNoticeDungeon(self):
		data=self.base_data('GetNoticeDungeon',2)
		return self.callAPI(self.c2_api,data)

	def GetNoticeChat(self):
		data=self.base_data('GetNoticeChat',2)
		return self.callAPI(self.c2_api,data)

	def getMentorRecommend(self):
		data=self.base_data('getMentorRecommend',2)
		return self.callAPI(self.c2_api,data)

	def GetNpcFriendList(self):
		data=self.base_data('GetNpcFriendList',2)
		return self.callAPI(self.c2_api,data)

	def GetWizardInfo(self):
		data=self.base_data('GetWizardInfo',2)
		return self.callAPI(self.c2_api,data)

	def CheckDailyReward(self):
		data=self.base_data('CheckDailyReward',2)
		return self.callAPI(self.c2_api,data)

	def gettrialtowerupdateremained(self):
		data=self.base_data('gettrialtowerupdateremained',2)
		return self.callAPI(self.c2_api,data)

	def GetShopInfo(self):
		data=self.base_data('GetShopInfo',2)
		return self.callAPI(self.c2_api,data)

	def GetDimensionHoleDungeonClearList(self):
		data=self.base_data('GetDimensionHoleDungeonClearList',2)
		return self.callAPI(self.c2_api,data)

	def getBattleOptionList(self):
		data=self.base_data('getBattleOptionList',2)
		return self.callAPI(self.c2_api,data)

	def receiveDailyRewardNewUser(self):
		data=self.base_data('receiveDailyRewardNewUser',2)
		return self.callAPI(self.c2_api,data)

	def GetFriendList(self):
		data=self.base_data('GetFriendList',2)
		return self.callAPI(self.c2_api,data)

	def GetFriendRequestSend(self):
		data=self.base_data('GetFriendRequestSend',2)
		return self.callAPI(self.c2_api,data)

	def SendDailyGift(self,friend_list):
		data=OrderedDict([('command','SendDailyGift'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('friend_list',friend_list)])
		return self.callAPI(self.c2_api,data)

	def AddFriendRequestByUid(self,uid):
		data=OrderedDict([('command','AddFriendRequestByUid'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('uid',uid)])
		return self.callAPI(self.c2_api,data)

	def GetFriendRecommended(self,show_more=0):
		data=OrderedDict([('command','GetFriendRecommended'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('show_more',show_more)])
		return self.callAPI(self.c2_api,data)

	def updateBattleOptionList(self,battle_option_list=[]):
		data=OrderedDict([('command','updateBattleOptionList'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_option_list',battle_option_list)])
		return self.callAPI(self.c2_api,data)

	def DoRandomWishItem(self,item_list_version,building_id):
		data=OrderedDict([('command','DoRandomWishItem'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('item_list_version',item_list_version),('island_id',1),('building_id',building_id),('pos_x',16),('pos_y',9),('cash_used',0)])
		return self.callAPI(self.c2_api,data)

	def SetDefenseUnits(self,unit_id_list):
		data=OrderedDict([('command','SetDefenseUnits'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('unit_id_list',unit_id_list)])
		return self.callAPI(self.c2_api,data)

	def CheckCandidateUid(self,candidate_uid):
		data=OrderedDict([('command','CheckCandidateUid'),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('wizard_id',self.wizard_id),('game_index',self.game_index),('uid',self.uid),('candidate_uid',candidate_uid),('session_key',self.getUID())])
		return self.callAPI(self.c2_api,data)

	def ProcessGuestTransition(self,candidate_uid,sessionkey):
		data=OrderedDict([('command','ProcessGuestTransition'),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',candidate_uid),('wizard_id',self.wizard_id),('uid',self.uid),('did',self.did),('game_index',self.game_index),('candidate_uid',candidate_uid),('use_old',0),('session_key',sessionkey)])
		return self.callAPI(self.c2_api,data)

	def SetRecentDecks(self,deck_list=[]):
		data=OrderedDict([('command','SetRecentDecks'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('app_version',self.app_version),('game_index',self.game_index),('deck_list',deck_list)])
		return self.callAPI(self.c2_api,data)

	def SacrificeUnit_V3(self,target_unit_id,building_id,island_id,pos_x,pos_y,source_unit_list=[]):
		data=OrderedDict([('command','SacrificeUnit_V3'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('target_unit_id',target_unit_id),('island_id',island_id),('building_id',building_id),('pos_x',pos_x),('pos_y',pos_y),('source_unit_list',source_unit_list),('source_item_list',[]),('source_storage_list',[])])
		return self.callAPI(self.c2_api,data)

	def CheckUnitCollection(self,unit_master_id_list=[]):
		data=OrderedDict([('command','CheckUnitCollection'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('unit_master_id_list',unit_master_id_list)])
		return self.callAPI(self.c2_api,data)

	def SetWizardName(self,wizard_name):
		self.log('new name:%s'%(wizard_name))
		data=OrderedDict([('command','SetWizardName'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('wizard_name',wizard_name.title())])
		return self.callAPI(self.c2_api,data)

	def WriteClientLog(self,logdata):
		data=OrderedDict([('command','WriteClientLog'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('logdata',logdata)])
		return self.callAPI(self.c2_api,data)

	def GetContentsUpdateNotice(self,lang='en'):
		data=OrderedDict([('command','GetContentsUpdateNotice'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('app_version',self.app_version),('lang',lang)])
		return self.callAPI(self.c2_api,data)

	def UpdateEventStatus(self,event_id):
		if event_id in self.event_id_list:
			return True
		data=OrderedDict([('command','UpdateEventStatus'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('event_id',event_id)])
		return self.callAPI(self.c2_api,data)

	def UpgradeDeco(self,deco_id):
		data=OrderedDict([('command','UpgradeDeco'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('deco_id',deco_id)])
		return self.callAPI(self.c2_api,data)

	def GetEventTimeTable(self,lang=1):
		data=OrderedDict([('command','GetEventTimeTable'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('lang',lang),('app_version',self.app_version)])
		return self.callAPI(self.c2_api,data)

	def GetArenaWizardList(self,refresh=0):
		data=OrderedDict([('command','GetArenaWizardList'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('refresh',refresh),('cash_used',0)])
		return self.callAPI(self.c2_api,data)

	def WorldRanking(self):
		data=OrderedDict([('command','WorldRanking'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime())])
		return self.callAPI(self.c2_api,data)

	def GetArenaUnitList(self,opp_wizard_id):
		data=OrderedDict([('command','GetArenaUnitList'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('opp_wizard_id',opp_wizard_id)])
		return self.callAPI(self.c2_api,data)

	def Harvest(self,building_id):
		self.log('harvesting from:%s'%(building_id))
		data=OrderedDict([('command','Harvest'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('building_id',building_id)])
		return self.callAPI(self.c2_api,data)

	def TriggerShopItem(self,trigger_id):
		data=OrderedDict([('command','TriggerShopItem'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('trigger_id',trigger_id)])
		return self.callAPI(self.c2_api,data)

	def UpdateAchievement(self,ach_list):
		data=OrderedDict([('command','UpdateAchievement'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('ach_list',ach_list)])
		return self.callAPI(self.c2_api,data)

	def ActivateQuests(self,quests):
		data=OrderedDict([('command','ActivateQuests'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('quests',quests)])
		return self.callAPI(self.c2_api,data)

	def UpdateDailyQuest(self,quests):
		data=OrderedDict([('command','UpdateDailyQuest'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('quests',quests)])
		return self.callAPI(self.c2_api,data)

	def getUID(self):
		if hasattr(self,'session_key') and self.session_key is not None:	return str(self.session_key)
		if self.isHive:
			return str(self.session_key)
		else:
			return str(self.uid)

	def BattleScenarioStart(self,region_id,stage_no,difficulty,unit_id_list,mentor_helper_list=[]):
		data=OrderedDict([('command','BattleScenarioStart'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('region_id',region_id),('stage_no',stage_no),('difficulty',difficulty),('unit_id_list',unit_id_list),('helper_list',[]),('mentor_helper_list',mentor_helper_list),('npc_friend_helper_list',[]),('retry',0),('auto_repeat',0)])
		return self.callAPI(self.c2_api,data)

	def BattleArenaStart(self,opp_wizard_id,unit_id_list):
		data=OrderedDict([('command','BattleArenaStart'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('opp_wizard_id',opp_wizard_id),('unit_id_list',unit_id_list),('retry',0),('is_rooting',0),('multiplay',0)])
		return self.callAPI(self.c2_api,data)

	def BattleDungeonStart(self,dungeon_id,stage_id,unit_id_list):
		data=OrderedDict([('command','BattleDungeonStart'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('dungeon_id',dungeon_id),('stage_id',stage_id),('helper_list',[]),('mentor_helper_list',[]),('npc_friend_helper_list',[]),('unit_id_list',unit_id_list),('cash_used',0),('retry',0),('is_rooting',0),('auto_repeat',0)])
		return self.callAPI(self.c2_api,data)

	def BattleTrialTowerStart_v2(self,difficulty,floor_id,unit_id_list):
		data=OrderedDict([('command','BattleTrialTowerStart_v2'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('difficulty',difficulty),('floor_id',floor_id),('unit_id_list',unit_id_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleScenarioResult(self,battle_key,opp_unit_status_list,unit_id_list,position):
		data=OrderedDict([('command','BattleScenarioResult'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('win_lose',1),('opp_unit_status_list',opp_unit_status_list),('unit_id_list',unit_id_list),('position',position),('clear_time',random.randint(68370, 100000)),('auto_clear',0),('play_speed',3),('retry',0),('auto_repeat',0)])
		return self.callAPI(self.c2_api,data)

	def BattleArenaResult(self,battle_key,opp_unit_status_list,unit_id_list,win_lose=1):
		data=OrderedDict([('command','BattleArenaResult'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('win_lose',win_lose),('opp_unit_status_list',opp_unit_status_list),('unit_id_list',unit_id_list),('retry',0),('is_rooting',0),('clear_time',random.randint(68370, 100000)),('auto_clear',0),('play_speed',3),('multiplay',0)])
		return self.callAPI(self.c2_api,data)

	def BattleDungeonResult(self,battle_key,dungeon_id,stage_id,unit_id_list,opp_unit_status_list):
		data=OrderedDict([('command','BattleDungeonResult'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('dungeon_id',dungeon_id),('stage_id',stage_id),('win_lose',1),('unit_id_list',unit_id_list),('opp_unit_status_list',opp_unit_status_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleDungeonResult_V2(self,battle_key,dungeon_id,stage_id,unit_id_list,opp_unit_status_list):
		data=OrderedDict([('command','BattleDungeonResult_V2'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('dungeon_id',dungeon_id),('stage_id',stage_id),('win_lose',1),('unit_id_list',unit_id_list),('opp_unit_status_list',opp_unit_status_list),('island_id',1),('pos_x',21),('pos_y',23),('clear_time',random.randint(68370, 100000)),('auto_clear',1),('play_speed',3),('retry',0),('leader_exist',1),('is_rooting',0),('auto_repeat',0)])
		return self.callAPI(self.c2_api,data)

	def BattleTrialTowerResult_v2(self,battle_key,difficulty,floor_id,unit_id_list,opp_unit_status_list):
		data=OrderedDict([('command','BattleTrialTowerResult_v2'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('difficulty',difficulty),('floor_id',floor_id),('win_lose',1),('unit_id_list',unit_id_list),('opp_unit_status_list',opp_unit_status_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def Summon(self,mode):
		for building in self.user['building_list']:
			if building['building_master_id'] ==2:
				building_id=building['building_id']
		self.SummonUnit(building_id,mode,[{"island_id":1,"pos_x":7,"pos_y":7,"unit_master_id":10602}])

	def useAllScrolls(self):
		for scroll in self.user['inventory_info']:
			if scroll['item_master_type']==9 and scroll['item_quantity']>=1:
				for i in range(scroll['item_quantity']):
					if scroll['item_master_id']==1:
						self.Summon(1)
					if scroll['item_master_id']==3:
						self.Summon(7)

	def SummonUnit(self,building_id,mode,pos_arr):
		data=OrderedDict([('command','SummonUnit'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('building_id',building_id),('mode',mode),('pos_arr',pos_arr)])
		res=self.callAPI(self.c2_api,data)
		if res and 'unit_list' in res:
			for x in res['unit_list']:
				u=self.getUnit(x['unit_master_id'])
				if u['base_class']>=5:
					if not hasattr(self,'five'):
						self.five=1
					else:
						self.five+=1
				self.log('%s %s* lvl:%s/%s exp:%s'%(self.getText(2,x['unit_master_id']),u['base_class'],x['unit_level'],u['max_level'],x['experience']))
		return res

	def EquipRune(self,rune_id,unit_id):
		data=OrderedDict([('command','EquipRune'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('rune_id',rune_id),('unit_id',unit_id)])
		return self.callAPI(self.c2_api,data)

	def UpgradeRune(self,rune_id,upgrade_curr,cash_used=0,stone_used=0):
		data=OrderedDict([('command','UpgradeRune'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('rune_id',rune_id),('upgrade_curr',upgrade_curr),('cash_used',cash_used),('stone_used',stone_used)])
		return self.callAPI(self.c2_api,data)

	def BuyShopItem(self,item_id,island_id,pos_x,pos_y):
		data=OrderedDict([('command','BuyShopItem'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('item_id',item_id),('island_id',island_id),('pos_x',pos_x),('pos_y',pos_y)])
		return self.callAPI(self.c2_api,data)

	def ClaimAchievementReward(self,ach_id,activate_quest_list=[],target_unit_id=None):
		if target_unit_id:
			data=OrderedDict([('command','ClaimAchievementReward'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('ach_id',ach_id),('activate_quest_list',activate_quest_list),('target_unit_id',target_unit_id)])
		else:
			data=OrderedDict([('command','ClaimAchievementReward'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('ach_id',ach_id),('activate_quest_list',activate_quest_list)])
		return self.callAPI(self.c2_api,data)

	def RewardDailyQuest(self,quest_id):
		data=OrderedDict([('command','RewardDailyQuest'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('quest_id',quest_id)])
		return self.callAPI(self.c2_api,data)

	def SacrificeUnit(self,target_id,source_list):
		data=OrderedDict([('command','SacrificeUnit'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('target_id',target_id),('island_id','1'),('building_id','0'),('pos_x','8'),('pos_y','14'),('source_list',source_list)])
		return self.callAPI(self.c2_api,data)

	def ReceiveMail(self,mail_id_list):
		data=OrderedDict([('command','ReceiveMail'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('mail_id_list',mail_id_list),('island_id','1'),('pos_x','19'),('pos_y','27')])
		return self.callAPI(self.c2_api,data)

	def GetWorldBossStatus(self,worldboss_id):
		data=OrderedDict([('command','GetWorldBossStatus'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('worldboss_id',worldboss_id)])
		return self.callAPI(self.c2_api,data)

	def createMentoring(self,target_wizard_id):
		data=OrderedDict([('command','createMentoring'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('target_wizard_id',target_wizard_id),('type',1),('ignore_attend',0)])
		return self.callAPI(self.c2_api,data)

	def CleanObstacle(self,obstacle_id):
		data=OrderedDict([('command','CleanObstacle'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('obstacle_id',obstacle_id)])
		return self.callAPI(self.c2_api,data)

	def setUser(self,input):
		if 'event_id_list' in input:	self.event_id_list=set(input['event_id_list'])
		if 'unit_list' in input and 'runes' in input:	self.user=input
		if 'scenario_list' in input:	self.scenario_list=input['scenario_list']
		self.wizard_id=input['wizard_info']['wizard_id']
		#self.log('wizard_id:%s'%(self.wizard_id))

	def updateWizard(self,input):
		if hasattr(self, 'user'):
			self.user['wizard_info']=input
			self.log(self.getUserInfo())

	def getUserInfo(self):
		#return 'id:%s username:%s energy:%s mana:%s crystal:%s level:%s'%(self.user['wizard_info']['wizard_id'],self.user['wizard_info']['wizard_name'],self.user['wizard_info']['wizard_energy'],self.user['wizard_info']['wizard_mana'],self.user['wizard_info']['wizard_crystal'],self.user['wizard_info']['wizard_level'])
		if not hasattr(self,'user'):
			self.log('[-] did not login')
			exit(1)
		return 'username:%s energy:%s mana:%s crystal:%s level:%s'%(self.user['wizard_info']['wizard_name'],self.user['wizard_info']['wizard_energy'],self.user['wizard_info']['wizard_mana'],self.user['wizard_info']['wizard_crystal'],self.user['wizard_info']['wizard_level'])

	def GuestLogin(self):
		data=OrderedDict([('command','GuestLogin'),('game_index',self.game_index),('proto_ver',self.proto_ver),('app_version',self.app_version),('infocsv',self.infocsv),('uid',self.uid),('channel_uid',self.uid),('did',self.did),('push',1),('is_emulator',0),('is_rooting',0),('country','RU'),('lang','eng'),('lang_game',1),('mac_address','02:00:00:00:00:00'),('device_name','iPad711'),('os_version','14.4'),('token','0000000000000000000000000000000000000000000000000000000000000000'),('idfv',self.idfa),('adid','00000000-0000-0000-0000-000000000000'),('create_if_not_exist',1),('is_jailbroken',0),('ag_cert_result',0),('ag_ucid','')])
		res= self.callAPI(self.c2_api,data)
		self.log(self.getUserInfo())
		return res

	def login(self):
		self.getServerStatus()
		self.getVersionInfo()
		self.CheckLoginBlock()
		if self.isHive:
			res= self.HubUserLogin()
		else:
			res= self.GuestLogin()
		self.ReceiveDailyRewardSpecial()
		self.receiveDailyRewardInactive()
		self.receiveDailyRewardNewUser()
		#self.ReceiveDailyRewardSpecial()
		return res

	def HubUserLogin(self):
		data=OrderedDict([('command','HubUserLogin'),('game_index',self.game_index),('proto_ver',self.proto_ver),('app_version',self.app_version),('session_key',self.getUID()),('infocsv',self.infocsv),('uid',self.uid),('channel_uid',self.uid),('did',self.did),('id',self._id),('email',self.email),('push',1),('is_emulator',0),('is_rooting',0),('country','RU'),('lang','eng'),('lang_game',1),('mac_address','02:00:00:00:00:00'),('device_name','iPad7,11'),('os_version','14.4'),('token','0000000000000000000000000000000000000000000000000000000000000000'),('idfv','00000000-0000-0000-0000-000000000000'),('adid','00000000-0000-0000-0000-000000000000'),('create_if_not_exist',1),('is_jailbroken',0),('ag_cert_result',0),('ag_ucid','')])
		res= self.callAPI(self.c2_api,data)
		self.save(json.dumps(res),'w_%s.txt'%(self.wizard_id))
		self.log(self.getUserInfo())
		return res

	def parseBattleStart(self,input,kind=0):
		battle_key=input['battle_key']
		opp_unit_status_list=[]
		if kind==1:
			for i in input['opp_unit_list']:
				opp_unit_status_list.append({'unit_id':i['unit_info']['unit_id'],'result':2})
		elif kind==0:
			for round in input['opp_unit_list']:
				for i in round:
					opp_unit_status_list.append({'unit_id':i['unit_id'],'result':2})
		elif kind==2:
			for round in input['dungeon_unit_list']:
				for i in round:
					opp_unit_status_list.append({'unit_id':i['unit_id'],'result':2})
		elif kind==4:
			for round in input['trial_tower_unit_list']:
				for i in round:
					opp_unit_status_list.append({'unit_id':i['unit_id'],'result':2})
		elif kind==3:
			for i in range(255):
				opp_unit_status_list.append({'unit_id':i,'result':2})
		return battle_key,opp_unit_status_list

	def parseBattleResult(self,input,extra=''):
		self.log('quest finished, win:%s extra:%s'%(input['win_lose'],extra))
		#self.log('rewards:%s'%(input['reward']))

	def makeUnitList(self,old):
		res=[]
		for idx,val in enumerate(old):
			res.append({'unit_id':val['unit_id'],'pos_id':idx+1})
		return res

	def getTeam(self,n=4,useMin=False):
		unit_id_list=[]
		units=self.getMaxUnit('class')
		if useMin:	units=self.getMinUnit()
		for x in units:
			if len(unit_id_list)<n:
				#u=self.getUnit(x['unit_master_id'])
				#self.log('%s %s* lvl:%s/%s exp:%s'%(self.getText(2,x['unit_master_id']),u['base_class'],x['unit_level'],u['max_level'],x['experience']))
				unit_id_list.append({'unit_id':int(x['unit_id'])})
		if len(unit_id_list)==0:
			print 'units missing'
			exit(1)
		return unit_id_list

	def exportUnits(self):
		units=self.getMaxUnit('class')
		for x in units:
				u=self.getUnit(x['unit_master_id'])
				self.log('%s %s* lvl:%s/%s exp:%s'%(self.getText(2,x['unit_master_id']),u['base_class'],x['unit_level'],u['max_level'],x['experience']))

	def doMission(self,region_id,stage_no,difficulty=1,exp=False,skipDone=False,useMin=False):
		self.legitarena()
		if skipDone:
			m='%s%s%s'%(region_id,stage_no,difficulty)
			if m in self.getcleared():
				#self.log('[-] already did this lvl.. %s'%m)
				return True

		if region_id==1 and difficulty==1:
			maxu=2
		else:
			maxu=4
		unit_id_list=self.getTeam(maxu,useMin)
		if hasattr(self,'refillEnergy') and self.user['wizard_info']['wizard_crystal']>=30 and self.user['wizard_info']['wizard_energy']<=3:
			self.BuyShopItem('100001',0,0,0)
		if region_id==9 and stage_no==7 and difficulty==1:
			for m in self.getMentorRecommend()['mentor_recommend']:
				if m['wizard_level']==50:
					self.createMentoring(m['wizard_id'])
					rep_unit_id=m['rep_unit_id']
					wizard_id=m['wizard_id']
					battle_start=self.BattleScenarioStart(region_id,stage_no,difficulty,unit_id_list,[{"wizard_id": wizard_id,"unit_id": rep_unit_id}])
					break
		else:
			battle_start=self.BattleScenarioStart(region_id,stage_no,difficulty,unit_id_list)
		if not battle_start:
			self.log('region:%s level:%s diff:%s not started'%(region_id,stage_no,difficulty))
			return
		if exp:
			battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,3)
		else:
			battle_key,opp_unit_status_list=self.parseBattleStart(battle_start)
		battle_end=self.BattleScenarioResult(battle_key,opp_unit_status_list,self.makeUnitList(unit_id_list),{"island_id":1,"pos_x":14,"pos_y":24})
		if battle_end:
			self.parseBattleResult(battle_end,'%s:%s:%s'%(region_id,stage_no,difficulty))
		if difficulty==1:
			self.sendevent('%s%s%s'%(region_id,stage_no,difficulty))
		self.refreshtoken()
		return battle_end

	def sendevent(self,m):
		r={'1141':578,'1301':60016,'211':506,'1261':587,'761':529,'661':552,'500101':10002,'131':502,'2801':1079,'871':23,'691':1070,'1071':28,'1371':34,'541':521,'341':543,'401':1034,'451':516,'811':554,'931':563,'1311':589,'1151':579,'671':553,'711':524,'121':501,'261':531,'500501':10010,'1061':573,'1011':568,'411':512,'531':520,'371':18,'921':562,'821':555,'1321':590,'1121':576,'501101':10016,'271':6,'1231':584,'831':556,'141':503,'521':519,'1251':586,'421':513,'1401':1005,'911':561,'1131':577,'361':545,'2601':1083,'301':1065,'500201':10004,'721':525,'1331':591,'510101':10024,'241':509,'101':60007,'841':557,'500601':10018,'1241':585,'511':518,'1001':1009,'431':514,'621':548,'501001':10014,'1221':583,'1341':592,'571':12,'331':542,'251':510,'171':505,'2201':1028,'851':558,'971':25,'731':526,'651':551,'1031':570,'311':540,'501':60014,'631':549,'751':528,'500301':10006,'561':533,'1351':593,'461':532,'2701':1072,'500901':10012,'161':530,'221':507,'1021':569,'961':566,'500701':10020,'861':559,'1101':60015,'151':504,'741':527,'1161':580,'551':522,'1211':582,'231':508,'641':550,'951':565,'441':515,'1111':575,'321':541,'2501':1087,'201':60009,'771':15,'1171':30,'1051':572,'1271':588,'611':547,'001':14,'500401':10008,'1041':571,'1601':1083,'1201':60017,'941':564,'471':9,'351':544,'1361':594,'801':1025}
		if m in r:
			self.UpdateEventStatus(event_id=r[m])

	def legitfarm(self):
		self.collectall()
		self.dowish()
		self.dowish()
		self.legitarena()

	def collectall(self):
		for x in self.user['building_list']:
			if 'harvest_available' in x and x['harvest_available']>=1:
				self.log('harvest from %s'%(x['building_id']))
				self.Harvest(building_id=x['building_id'])

	def canbeat(self,i):
		units=self.GetArenaUnitList(opp_wizard_id=i)['opp_unit_list']
		v=len(units)<=1
		lvls=[x['unit_info']['unit_level'] for x in units]
		v1=all(x<=16 for x in lvls)
		return v or v1

	def legitarena(self):
		if 'arena_energy' in self.user['wizard_info'] and self.user['wizard_info']['arena_energy']<=0:	return True
		res=self.GetArenaWizardList(refresh=0)['arena_list']
		didWin=False
		for x in res:
			if x['defeat']==1:	continue
			if self.canbeat(x['wizard_id']):
				if self.doArena(x['wizard_id']):
					self.log('[+] we did win!')
					didWin=True
				else:
					return True
		if not didWin:
			self.log('[-] did not win so we loose')
			self.doArena(x['wizard_id'],0)
			self.GetArenaWizardList(refresh=1)
		return self.legitarena()

	def unlockaiden(self):
		self.UpdateEventStatus(event_id=60006)
		self.UpdateEventStatus(event_id=1033)
		self.BuyShopItem(pos_x=6,pos_y=14,island_id=1,item_id=800009)
		self.UpdateEventStatus(event_id=1034)
		self.UpdateAchievement(ach_list=[{'current': 8, 'ach_id': 55, 'cond_id': 1}])
		self.BuyShopItem(pos_x=22,pos_y=11,island_id=1,item_id=800014)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 22, 'cond_id': 1}, {'current': 1, 'ach_id': 24, 'cond_id': 1}, {'current': 9, 'ach_id': 55, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1005)
		self.BuyShopItem(pos_x=22,pos_y=9,island_id=1,item_id=800014)
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 22, 'cond_id': 1}, {'current': 2, 'ach_id': 24, 'cond_id': 1}, {'current': 10, 'ach_id': 55, 'cond_id': 1}])
		self.BuyShopItem(pos_x=22,pos_y=7,island_id=1,item_id=800014)
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 24, 'cond_id': 1}])
		self.BuyShopItem(pos_x=9,pos_y=20,island_id=1,item_id=800029)
		self.UpdateEventStatus(event_id=1072)
		self.BuyIsland(island_id=3)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 54, 'cond_id': 1}])
		self.BuyIsland(island_id=4)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 56, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1073)
		self.UpdateEventStatus(event_id=1035)
		self.UpdateEventStatus(event_id=1054)
		self.UpdateEventStatus(event_id=26)
		self.UpdateEventStatus(event_id=27)

	def unlockvrof(self):
		self.UpdateEventStatus(event_id=1030)
		self.UpdateEventStatus(event_id=22)

	def unlocktamor(self):
		self.UpdateEventStatus(event_id=21)
		self.UpdateEventStatus(event_id=14)
		self.UpdateEventStatus(event_id=1020)
		self.BuyIsland(island_id=2)
		self.UpdateEventStatus(event_id=1019)
		self.UpdateEventStatus(event_id=1061)

	def unlockhydeni(self):
		self.UpdateEventStatus(event_id=13)
		self.UpdateEventStatus(event_id=19)
		self.UpdateEventStatus(event_id=1026)
		self.UpdateEventStatus(event_id=50015)
		self.UpdateEventStatus(event_id=50068)

	def unlocktelain(self):
		self.UpdateEventStatus(event_id=60025)
		self.UpdateEventStatus(event_id=1010)
		self.BuyShopItem(pos_x=17,pos_y=7,island_id=1,item_id=800010)
		self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 55, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1009)
		self.UpdateEventStatus(event_id=1056)
		self.UpdateEventStatus(event_id=10)

	def unlockwhite(self):
		self.UpdateEventStatus(event_id=1008)
		self.BuyShopItem(pos_x=22,pos_y=13,island_id=1,item_id=800011)
		self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 55, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1007)
		self.UpdateEventStatus(event_id=1055)
		self.UpdateEventStatus(event_id=8)

	def unlokcksiz(self):
		self.UpdateEventStatus(event_id=5)
		self.UpdateEventStatus(event_id=60018)
		self.TriggerShopItem(trigger_id=251)
		self.GetShopInfo()
		self.UpdateEventStatus(event_id=11003)

	def unlockruins(self):
		self.UpdateEventStatus(event_id=509)
		self.UpdateEventStatus(event_id=508)
		self.GetArenaLog()
		self.UpdateEventStatus(event_id=506)
		self.UpdateEventStatus(event_id=511)
		self.UpdateEventStatus(event_id=510)
		self.UpdateEventStatus(event_id=531)
		self.UpdateEventStatus(event_id=507)
		self.UpdateEventStatus(event_id=6)
		self.UpdateEventStatus(event_id=60005)
		self.UpdateEventStatus(event_id=17)
		self.UpdateEventStatus(event_id=100)
		self.UpdateEventStatus(event_id=101)
		self.UpdateEventStatus(event_id=103)
		self.UpdateEventStatus(event_id=104)
		self.UpdateEventStatus(event_id=104)

	def getcleared(self):
		res=set()
		for x in self.scenario_list:
			region_id=x['region_id']
			difficulty=x['difficulty']
			for j in x['stage_list']:
				res.add('%s%s%s'%(region_id,j['stage_no'],difficulty))
		return res

	def removeAllObstacle(self):
		for obstacle in self.user['obstacle_list']:
			self.CleanObstacle(obstacle['obstacle_id'])

	def doArena(self,opp_wizard_id,win_lose=1):
		if self.user['wizard_info']['arena_energy']<=0:	return
		unit_id_list=self.getTeam(4)
		battle_start=self.BattleArenaStart(opp_wizard_id,unit_id_list)
		if not battle_start:
			self.log('dont have battle data')
			return
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,1)
		battle_end=self.BattleArenaResult(battle_key,opp_unit_status_list,unit_id_list,win_lose=win_lose)
		if battle_end:
			self.parseBattleResult(battle_end,opp_wizard_id)
		return battle_end

	def doDungeon(self,dungeon_id,stage_id):
		unit_id_list=self.getTeam(5)
		if hasattr(self,'refillEnergy') and self.user['wizard_info']['wizard_crystal']>=30 and self.user['wizard_info']['wizard_energy']<=8:
			self.BuyShopItem('100001',0,0,0)
		battle_start=self.BattleDungeonStart(dungeon_id,stage_id,unit_id_list)
		if not battle_start:
			self.log('dont have battle data')
			return
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,2)
		battle_end=self.BattleDungeonResult_V2(battle_key,dungeon_id,stage_id,unit_id_list,opp_unit_status_list)
		if battle_end:
			self.parseBattleResult(battle_end,'%s:%s'%(dungeon_id,stage_id))
		return battle_end

	def doTower(self,floor_id,difficulty):
		unit_id_list=self.getTeam(5)
		if hasattr(self,'refillEnergy') and self.user['wizard_info']['wizard_crystal']>=30 and self.user['wizard_info']['wizard_energy']<=8:
			self.BuyShopItem('100001',0,0,0)
		battle_start=self.BattleTrialTowerStart_v2(difficulty,floor_id,unit_id_list)
		if not battle_start:
			self.log('dont have battle data')
			return
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,4)
		battle_end=self.BattleTrialTowerResult_v2(battle_key,difficulty,floor_id,unit_id_list,opp_unit_status_list)
		if battle_end:
			self.parseBattleResult(battle_end,'%s:%s'%(floor_id,difficulty))
		return battle_end

	def repeatAreana(self):
		if self.user['wizard_info']['arena_energy']>=1:
			hasVic=True
			refresh=0
			repeat=0
			while(hasVic):
				if repeat>=4:
					break
				arena_list=self.GetArenaWizardList(refresh)['arena_list']
				repeat+=1
				for wizard in arena_list:
					if self.user['wizard_info']['wizard_level']<=10:
						limit=15
					elif self.user['wizard_info']['wizard_level']>10 and self.user['wizard_info']['wizard_level']<=20:
						limit=22
					if wizard['defeat']==0 and wizard['wizard_level']<=limit:
						if not self.doArena(wizard['wizard_id']):
							hasVic=False
							break
						#else:
						#	self.log('killed %s lvl'%(wizard['wizard_level']))
						#	self.save('pvp:%s me:%s'%(wizard['wizard_level'],self.user['wizard_info']['wizard_level']),'arena.txt')
				refresh=1
		if hasattr(self,'IsBadBot') and self.user['wizard_info']['wizard_crystal']>=30 and self.user['wizard_info']['arena_energy']==0:
			self.BuyShopItem('300001',0,0,0)
			return self.repeatAreana()

	def getAllMail(self):
		mails=self.GetMailList()['mail_list']
		done=[]
		for mail in mails:
			if mail['item_master_type']<>23:
				done.append({"mail_id":mail['mail_id']})
		self.ReceiveMail(done)

	def getAllMailF(self,item_master_id=103):
		mails=self.GetMailList()['mail_list']
		done=[]
		for mail in mails:
			if 'item_master_id' in mail and mail['item_master_id']==item_master_id:	continue
			if 'rune_box_id' in mail and mail['rune_box_id']==23:
				self.ReceiveMail([{"mail_id":mail['mail_id'],"rune_box_id":5408}])
				continue
			elif 'rune_box_id' in mail:
				continue
			#done.append({"mail_id":mail['mail_id']})
			self.ReceiveMail([{"mail_id":mail['mail_id']}])
		#self.ReceiveMail(done)

	def getArenaWins(self):
		self.log('%s arena wins'%(self.user['pvp_info']['arena_win']))

	def checkArena(self):
		if hasattr(self,'canArena'):
			self.repeatAreana()

	def unlockAreana(self):
		for i in range(50):
			self.UpdateEventStatus(i)

	def completeDungeon(self,dungeon_id,skip=0):
		for i in range(10):
			if (i+1)<=skip:
				continue
			if not self.doDungeon(dungeon_id,i+1):
				break
			self.checkArena()

	def completeTower(self,difficulty,skip=0):
		for i in range(100):
			if (i+1)<=skip:
				continue
			self.doTower(i+1,difficulty)
			self.checkArena()

	def completeRegion(self,region,diff=1,skip=0,skipDone=True):
		for i in range(7):
			if (i+1)<=skip:
				continue
			if not self.doMission(region,i+1,diff,skipDone=skipDone):	return False
			self.checkArena()
			self.legitarena()
		return True

	def completeDaily(self):
		done=[]
		quest_list=self.GetDailyQuests()['quest_list']
		for quest in quest_list:
			done.append({"quest_id":quest['quest_id'],"progressed":quest['required']+1})
		self.UpdateDailyQuest(done)

	def completeAch(self):
		done=[]
		for i in range(1,20):
			done.append({"ach_id":i,"cond_id":1,"current":10})
		self.UpdateAchievement(done)

	def getMaxUnit(self,f='unit_level',s=None):
		r=self.getUnits()
		if s is not None:
			r.sort(key=lambda x: (x[f],x[s]), reverse=True)
		else:
			r.sort(key=lambda x: x[f], reverse=True)
		return r

	def getMinUnit(self,f='experience',lvl=None,skip=True):
		r=self.getUnits(skip)
		if lvl is not None:
			r.sort(key=lambda x: x[f]==lvl, reverse=False)
		else:
			r.sort(key=lambda x: x[f], reverse=False)
		return r

	def refreshtoken(self):
		if self.isHive:
			res= self.HubUserLogin()
		else:
			res= self.GuestLogin()

	def findUnit(self,u):
		r=self.getUnits()
		for x in r:
			if u==x['unit_master_id']:	return x
		return None

	def getUnits(self,skip=True):
		res=[]
		for x in self.user['unit_list']:
			if skip and x['atk']<=10:	continue
			res.append(x)#['unit_id'])
			#u=self.getUnit(x['unit_master_id'])
			#self.log('%s %s* lvl:%s/%s exp:%s'%(self.getText(2,x['unit_master_id']),u['base_class'],x['unit_level'],u['max_level'],x['experience']))
		return res

	def getBuilding(self,i):
		for x in self.user['building_list']:
			if x['building_master_id'] ==i:	return x
		return None

	def dowish(self):
		if not self.getBuilding(10):	return
		if self.user['wish_list']['trial_remained']>=1:
			self.log('doing wish')
			self.DoRandomWishItem(building_id=self.getBuilding(10),item_list_version=self.user['wish_list']['item_list_version'])

	def powerMonster(self,end=0):
		for unit in self.user['unit_list']:
			if len(unit['runes'])>=1:
				if type(unit['runes'])==list:
					for idx,rune in enumerate(unit['runes']):
						upgrade_curr=unit['runes'][idx]['upgrade_curr']
						for i in range(end):
							if (i+1)<=upgrade_curr:
								continue
							if self.UpgradeRune(unit['runes'][idx]['rune_id'],upgrade_curr):
								upgrade_curr+=1
				else:
					for rune in unit['runes']:
						upgrade_curr=unit['runes'][rune]['upgrade_curr']
						for i in range(end):
							if (i+1)<=upgrade_curr:
								continue
							if self.UpgradeRune(unit['runes'][rune]['rune_id'],upgrade_curr):
								upgrade_curr+=1

	def completeTutorial(self,q=None):
		if hasattr(self,'user'):
			if self.user['wizard_info']['wizard_mana']<>13000:
				return
		self.login()
		self.GetDailyQuests()
		self.GetMiscReward()
		self.ReceiveDailyRewardSpecial()
		self.GetArenaLog()
		self.GetContentsUpdateNotice(lang='en')
		self.getUnitStorageList()
		self.getUpdatedDataBeforeWebEvent()
		self.GetMailList()
		self.GetFriendRequest()
		self.GetChatServerInfo()
		self.GetRtpvpQuests()
		self.getRtpvpRejoinInfo()
		self.WriteClientLog(logdata={'battle': 0, 'type': 'prequel', 'message': 'start', 'data': ''})
		self.WriteClientLog(logdata={'battle': 17, 'type': 'prequel', 'message': 'finish', 'data': ''})
		self.WriteClientLog(logdata={'battle': 17, 'type': 'intro', 'message': 'start', 'data': ''})
		self.WriteClientLog(logdata={'battle': 17, 'type': 'intro', 'message': 'finish', 'data': ''})
		self.SetWizardName(wizard_name=Tools().rndUser())
		self.UpdateEventStatus(event_id=1500)
		self.GetEventTimeTable(lang=1)
		self.getBattleOptionList()
		self.receiveDailyRewardNewUser()
		building_id=[x['building_id'] for x in self.user['building_list'] if 'harvest_max' in x][0]
		self.Harvest(building_id=building_id)
		self.UpdateEventStatus(event_id=1085)
		self.TriggerShopItem(trigger_id=20)
		self.UpdateEventStatus(event_id=60021)
		self.TriggerShopItem(trigger_id=364)
		self.UpdateEventStatus(event_id=60070)
		sac_unit=self.SummonUnit(pos_arr=[{'island_id': 1, 'pos_x': 10, 'pos_y': 4, 'unit_master_id': 10602}],mode=1,building_id=self.getBuilding(2))['defense_unit_list'][0]['unit_id']
		self.GetShopInfo()
		self.GetShopInfo()
		self.UpdateEventStatus(event_id=1501)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 2, 'cond_id': 2}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 6, 'cond_id': 2}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 15, 'cond_id': 2}])
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 55, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 177, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 179, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 178, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 299, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 304, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 300, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 303, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 424, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 425, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 426, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 497, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 498, 'cond_id': 1}])
		self.CheckUnitCollection(unit_master_id_list=[1000102, 1000204])
		defense_unit_list=self.SummonUnit(pos_arr=[{'island_id': 1, 'pos_x': 6, 'pos_y': 19, 'unit_master_id': 10101}],mode=2,building_id=self.getBuilding(2))
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 2, 'cond_id': 1}, {'current': 1, 'ach_id': 6, 'cond_id': 1}, {'current': 1, 'ach_id': 15, 'cond_id': 1}, {'current': 1, 'ach_id': 33, 'cond_id': 1}, {'current': 1, 'ach_id': 478, 'cond_id': 1}])
		self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 3}])
		self.UpdateEventStatus(event_id=1502)
		self.GetDimensionHoleDungeonClearList()
		#self.GetWorldBossStatus(worldboss_id=10321)
		first_unit=defense_unit_list['unit_list'][0]['unit_id']
		unit_id_list=[]
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id']})
		unit_id_list.sort()
		self.SetRecentDecks(deck_list=[{'leader_unit_id': defense_unit_list['defense_unit_list'][0]['unit_id'], 'type': 1, 'sub_type': 2, 'unit_id_list': [defense_unit_list['defense_unit_list'][0]['unit_id'], defense_unit_list['defense_unit_list'][1]['unit_id'], 0, 0, 0, 0, 0, 0]}])
		battle_start=self.BattleScenarioStart(region_id=1,difficulty=1,unit_id_list=unit_id_list,stage_no=1)
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start)
		self.UpdateDailyQuest(quests=[{'progressed': 3, 'quest_id': 1}])
		self.UpdateEventStatus(event_id=50001)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 3, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=50035)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 3, 'cond_id': 2}])
		unit_id_list=[]
		pos=0
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id'],'pos_id':pos})
			pos+=1
		self.BattleScenarioResult(unit_id_list=unit_id_list,opp_unit_status_list=opp_unit_status_list,battle_key=battle_key,position={'island_id': 1, 'pos_x': 17, 'pos_y': 27})
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 8, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1503)
		self.UpdateEventStatus(event_id=1504)
		self.GetEventTimeTable(lang=1)
		defense_unit_list=self.SummonUnit(pos_arr=[{'island_id': 1, 'pos_x': 14, 'pos_y': 11, 'unit_master_id': 15203}],mode=1,building_id=self.getBuilding(2))
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 2, 'cond_id': 3}, {'current': 1, 'ach_id': 6, 'cond_id': 3}, {'current': 1, 'ach_id': 15, 'cond_id': 3}])
		self.UpdateDailyQuest(quests=[{'progressed': 2, 'quest_id': 3}])
		self.UpdateEventStatus(event_id=1506)
		self.UpdateEventStatus(event_id=1507)
		for rune in self.user['runes']:
			rune_id=rune['rune_id']
		self.EquipRune(rune_id=rune_id,unit_id=first_unit)
		self.UpgradeRune(cash_used=0,rune_id=rune_id,stone_used=0,upgrade_curr=0)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 25, 'cond_id': 1}])
		self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 4}])
		self.BuyShopItem(pos_x=22,pos_y=19,island_id=1,item_id=800020)
		self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 55, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=1508)
		self.UpdateEventStatus(event_id=1509)
		self.SacrificeUnit_V3(target_unit_id=sac_unit,pos_y=4,pos_x=10,island_id=1,building_id=0)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 13, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 6, 'cond_id': 2}, {'current': 1, 'ach_id': 31, 'cond_id': 1}])
		self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 2}])
		self.UpdateEventStatus(event_id=1510)
		self.UpdateEventStatus(event_id=2)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 263, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=41)
		self.UpdateEventStatus(event_id=50020)
		unit_id_list=[]
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id']})
		unit_id_list.sort()
		battle_start=self.BattleScenarioStart(region_id=1,difficulty=1,unit_id_list=unit_id_list,stage_no=2)
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start)
		unit_id_list=[]
		pos=0
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id'],'pos_id':pos})
			pos+=1
		self.SetRecentDecks(deck_list=[{'leader_unit_id': defense_unit_list['defense_unit_list'][1]['unit_id'], 'type': 1, 'sub_type': 3, 'unit_id_list': [defense_unit_list['defense_unit_list'][0]['unit_id'], defense_unit_list['defense_unit_list'][1]['unit_id'], defense_unit_list['defense_unit_list'][2]['unit_id'], 0, 0, 0, 0, 0]}])
		self.UpdateDailyQuest(quests=[{'progressed': 6, 'quest_id': 1}])
		self.BattleScenarioResult(unit_id_list=unit_id_list,opp_unit_status_list=opp_unit_status_list,battle_key=battle_key,position={'island_id': 1, 'pos_x': 14, 'pos_y': 26})
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 177, 'cond_id': 1}, {'current': 2, 'ach_id': 178, 'cond_id': 1}, {'current': 2, 'ach_id': 179, 'cond_id': 1}, {'current': 2, 'ach_id': 299, 'cond_id': 1}, {'current': 2, 'ach_id': 300, 'cond_id': 1}, {'current': 2, 'ach_id': 303, 'cond_id': 1}, {'current': 2, 'ach_id': 304, 'cond_id': 1}, {'current': 2, 'ach_id': 305, 'cond_id': 1}, {'current': 2, 'ach_id': 497, 'cond_id': 1}, {'current': 2, 'ach_id': 498, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=501)
		self.GetNpcFriendList()
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 263, 'cond_id': 1}])
		self.GetEventTimeTable(lang=1)
		self.UpdateEventStatus(event_id=50029)
		self.refreshtoken()
		#part2
		self.doMission(region_id=1,difficulty=1,stage_no=3)
		self.UpdateDailyQuest(quests=[{'progressed': 9, 'quest_id': 1}])
		self.UpdateEventStatus(event_id=502)
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 263, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=50065)
		self.doMission(region_id=1,difficulty=1,stage_no=4)
		self.UpdateDailyQuest(quests=[{'progressed': 12, 'quest_id': 1}])
		self.GetNpcFriendList()
		self.UpdateEventStatus(event_id=503)
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 177, 'cond_id': 1}, {'current': 3, 'ach_id': 178, 'cond_id': 1}, {'current': 3, 'ach_id': 179, 'cond_id': 1}, {'current': 3, 'ach_id': 299, 'cond_id': 1}, {'current': 3, 'ach_id': 300, 'cond_id': 1}, {'current': 3, 'ach_id': 303, 'cond_id': 1}, {'current': 3, 'ach_id': 304, 'cond_id': 1}, {'current': 3, 'ach_id': 305, 'cond_id': 1}, {'current': 3, 'ach_id': 497, 'cond_id': 1}, {'current': 3, 'ach_id': 498, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 263, 'cond_id': 1}])
		self.doMission(region_id=1,difficulty=1,stage_no=5)
		self.UpdateDailyQuest(quests=[{'progressed': 15, 'quest_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 3, 'cond_id': 3}])
		self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 263, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=504)
		self.doMission(region_id=1,difficulty=1,stage_no=6)
		self.UpdateDailyQuest(quests=[{'progressed': 18, 'quest_id': 1}])
		self.UpdateEventStatus(event_id=530)
		self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 263, 'cond_id': 1}])
		self.doMission(region_id=1,difficulty=1,stage_no=7)
		self.UpdateDailyQuest(quests=[{'progressed': 20, 'quest_id': 1}])
		self.UpdateEventStatus(event_id=50022)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 88, 'cond_id': 1}])
		self.GetNpcFriendList()
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 177, 'cond_id': 1}, {'current': 4, 'ach_id': 178, 'cond_id': 1}, {'current': 4, 'ach_id': 179, 'cond_id': 1}, {'current': 4, 'ach_id': 299, 'cond_id': 1}, {'current': 4, 'ach_id': 300, 'cond_id': 1}, {'current': 4, 'ach_id': 303, 'cond_id': 1}, {'current': 4, 'ach_id': 304, 'cond_id': 1}, {'current': 4, 'ach_id': 305, 'cond_id': 1}, {'current': 4, 'ach_id': 497, 'cond_id': 1}, {'current': 4, 'ach_id': 498, 'cond_id': 1}])
		self.UpdateEventStatus(event_id=505)
		self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 263, 'cond_id': 1}, {'current': 1, 'ach_id': 20001, 'cond_id': 1}])
		self.ClaimAchievementReward(ach_id=263)
		self.UpdateEventStatus(event_id=3)
		self.GetEventTimeTable()
		self.UpdateEventStatus(event_id=5)
		self.UpdateEventStatus(event_id=60018)
		self.TriggerShopItem(trigger_id=251)
		self.GetShopInfo()
		self.UpdateEventStatus(event_id=11003)
		self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20002}],ach_id=20001)
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 21001, 'cond_id': 1}])
		self.getAllMailF()

		while(1):
			if not self.SummonUnit(pos_arr=[{'island_id': 1, 'pos_x': 0, 'pos_y': 16, 'unit_master_id': 0}],mode=2,building_id=self.getBuilding(2)):	break

		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 6, 'cond_id': 1}, {'current': 2, 'ach_id': 478, 'cond_id': 1}, {'current': 2, 'ach_id': 20002, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 6, 'cond_id': 3}, {'current': 1, 'ach_id': 33, 'cond_id': 3}, {'current': 1, 'ach_id': 476, 'cond_id': 1}, {'current': 3, 'ach_id': 20002, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 33, 'cond_id': 2}, {'current': 1, 'ach_id': 477, 'cond_id': 1}, {'current': 4, 'ach_id': 20002, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 477, 'cond_id': 1}, {'current': 5, 'ach_id': 20002, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 478, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 476, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 476, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 476, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 8, 'ach_id': 477, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 476, 'cond_id': 1}])
		self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 478, 'cond_id': 1}])

		if q is not None:
			candidate_uid=int(q.uid)
			self.CheckCandidateUid(candidate_uid=candidate_uid)
			sessionkey=q.bind()
			self.ProcessGuestTransition(candidate_uid=candidate_uid,sessionkey=sessionkey)
			self.HubUserLogin()
		if hasattr(self,'five') and self.five>=1:
			self.db.addAccount(self.wizard_id,self.user['wizard_info']['wizard_energy'],self.user['wizard_info']['wizard_mana'],self.user['wizard_info']['wizard_crystal'],self.user['wizard_info']['wizard_level'],self.uid,self.did)

	def getfood(self,classes=[1,2],skip=True):
		res=set()
		units=self.getMinUnit(skip=skip)
		for x in units:
			if x['class'] in classes:
				self.log('[+] found food %s %s* lvl:%s'%(self.getText(2,x['unit_master_id']),x['class'],x['unit_level']))
				defends=[j['unit_id'] for j in self.user['defense_unit_list']]
				if x['unit_id'] not in defends:
					res.add(x['unit_id'])
		return list(res)

	def feedunit(self,target_unit_id,n=1,skip=True):
		if n ==0:	return
		self.refreshtoken()
		if len(str(target_unit_id))>=10:
			target=target_unit_id
		else:
			target=self.findUnit(target_unit_id)['unit_id']
		foods= self.getfood(skip=skip)
		if len(foods)==0:
			self.log('no food..')
			return
		res=[]
		if n==5:	n-=1
		for x in foods[:n]:
			res.append({'unit_id': x})
		self.SacrificeUnit_V3(target_unit_id=target,pos_y=19,pos_x=6,island_id=1,source_unit_list=res,building_id=0)

	def upgraderu(self,rune_id,n=1):
		upgrade_curr=0
		while(upgrade_curr<n):
			res= self.UpgradeRune(rune_id=rune_id,stone_used=0,upgrade_curr=upgrade_curr)
			if res:
				upgrade_curr=res['rune']['upgrade_curr']
			else:
				return

	def upgraderunmonster(self,u=None,n=6):
		if u is not None:
			x=self.findUnit(u)
			for r in x['runes']:
				self.upgraderu(r['rune_id'],n)
		else:
			units=self.getMaxUnit('class')
			for x in units:
				if len(x['runes'])==6:
					for r in x['runes']:
						if 'rune_id' not in r:	continue
						if r['upgrade_curr']<n:
							self.upgraderu(r['rune_id'], n)

	def getrunes(self,setid):
		self.refreshtoken()
		res=set()
		did=set()
		for x in self.user['runes']:
			if x['set_id']==setid:
				if x['slot_no'] in did:	continue
				did.add(x['slot_no'])
				res.add(x['rune_id'])
		return res

	def getmaxu(self,f='class'):
		self.refreshtoken()
		x=self.getMaxUnit(f)[0]
		self.log('[+] found %s %s* lvl:%s'%(self.getText(2,x['unit_master_id']),x['class'],x['unit_level']))
		return x['unit_id']

	def dofriends(self):
		friends=self.GetFriendList()
		res=[]
		for f in friends['friend_list']:
			if f['next_gift_time']==0:
				res.append({'wizard_id': f['wizard_id']})
		if len(res)>=1:
			self.SendDailyGift(res)
		self.addfriends()

	def addfriends(self):
		did=[x['channel_uid'] for x in self.GetFriendRequestSend()['friend_req_list']]
		firstRound=True
		j=0
		for i in range(10):
			r=self.GetFriendRecommended(0 if firstRound else 1)
			if not r:	return
			firstRound=False
			for x in r['recommended_list']:
				if x['channel_uid'] in did:	continue
				did.append(x['channel_uid'])
				if self.AddFriendRequestByUid(x['channel_uid']):
					self.UpdateAchievement(ach_list=[{'current': j+1, 'ach_id': 20014, 'cond_id': 1}])
					j+=1

	def makemaster(self,skip=True):
		if not skip:
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20003}],ach_id=20002)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 21001, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50007)
			self.SummonUnit(pos_arr=[{'island_id': 1, 'pos_x': 3, 'pos_y': 5, 'unit_master_id': 0}],mode=1,building_id=self.getBuilding(2))
			self.UpdateDailyQuest(quests=[{'progressed': 3, 'quest_id': 3}])
			self.UpdateEventStatus(event_id=50023)
			self.UpdateEventStatus(event_id=50008)
			self.feedunit(10101,1)#-------------------------------------
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 14, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 31, 'cond_id': 1}, {'current': 1, 'ach_id': 20003, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 2, 'quest_id': 2}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20004}],ach_id=20003)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 21001, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50055)
			self.doMission(region_id=2,difficulty=1,stage_no=1)
			self.UpdateEventStatus(event_id=50019)
			self.UpdateEventStatus(event_id=506)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 20004, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 257, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50013)
			self.doMission(region_id=2,difficulty=1,stage_no=2)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 257, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=507)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 20004, 'cond_id': 1}])
			self.doMission(region_id=2,difficulty=1,stage_no=3)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 177, 'cond_id': 1}, {'current': 5, 'ach_id': 178, 'cond_id': 1}, {'current': 5, 'ach_id': 179, 'cond_id': 1}, {'current': 5, 'ach_id': 299, 'cond_id': 1}, {'current': 5, 'ach_id': 300, 'cond_id': 1}, {'current': 5, 'ach_id': 303, 'cond_id': 1}, {'current': 5, 'ach_id': 304, 'cond_id': 1}, {'current': 5, 'ach_id': 305, 'cond_id': 1}, {'current': 5, 'ach_id': 497, 'cond_id': 1}, {'current': 5, 'ach_id': 498, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 20004, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=508)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 257, 'cond_id': 1}])
			self.doMission(region_id=2,difficulty=1,stage_no=4)
			self.UpdateEventStatus(event_id=509)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 257, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 20004, 'cond_id': 1}])
			self.doMission(region_id=2,difficulty=1,stage_no=5)
			self.UpdateEventStatus(event_id=510)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 257, 'cond_id': 1}])
			self.doMission(region_id=2,difficulty=1,stage_no=6)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 257, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=531)
			self.UpdateEventStatus(event_id=60007)
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20005}],ach_id=20004)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 21001, 'cond_id': 1}])
			self.doMission(region_id=2,difficulty=1,stage_no=7)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 90, 'cond_id': 1}, {'current': 1, 'ach_id': 91, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=511)
			self.UpdateEventStatus(event_id=70001)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 257, 'cond_id': 1}, {'current': 1, 'ach_id': 20005, 'cond_id': 1}])
			self.ClaimAchievementReward(ach_id=257)
			self.UpdateEventStatus(event_id=6)
			self.UpdateEventStatus(event_id=17)
			self.UpdateEventStatus(event_id=100)
			self.UpdateEventStatus(event_id=101)
			self.UpdateEventStatus(event_id=103)
			self.UpdateEventStatus(event_id=104)
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20006}],ach_id=20005)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 21001, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50073)
			self.UpdateEventStatus(event_id=70005)
			self.UpdateEventStatus(event_id=1026)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 5, 'cond_id': 1}, {'current': 1, 'ach_id': 29, 'cond_id': 1}, {'current': 1, 'ach_id': 192, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50068)
			self.UpdateEventStatus(event_id=50015)
			self.UpdateEventStatus(event_id=50057)
			self.UpdateEventStatus(event_id=50070)
			self.UpdateEventStatus(event_id=50080)
			#self.EquipRune(rune_id=25040135228,unit_id=11274658287)
			self.getAllMailF()
			self.refreshtoken()
			runes=self.getrunes(8)
			maxunit=self.findUnit(19801)['unit_id']
			for r in runes:
				self.EquipRune(rune_id=r,unit_id=maxunit)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 29, 'cond_id': 1}, {'current': 1, 'ach_id': 20006, 'cond_id': 1}, {'current': 1, 'ach_id': 193, 'cond_id': 1}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20007}],ach_id=20006)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 21001, 'cond_id': 1}])
			for r in runes:
				self.upgraderu(r,6)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 25, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 2, 'quest_id': 4}])
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 25, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 3, 'quest_id': 4}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 173, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 26, 'cond_id': 1}, {'current': 1, 'ach_id': 20007, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 173, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 20007, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 173, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 173, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 20007, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 20007, 'cond_id': 1}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20008}],ach_id=20007)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 21001, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=80001)
			self.UpdateEventStatus(event_id=4)
			self.UpdateEventStatus(event_id=10001)
			self.doArena(opp_wizard_id=5001)
			self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 8}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 20008, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50005)
			self.UpdateEventStatus(event_id=10002)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 12, 'cond_id': 1}, {'current': 1, 'ach_id': 359, 'cond_id': 1}, {'current': 1, 'ach_id': 360, 'cond_id': 1}, {'current': 1, 'ach_id': 361, 'cond_id': 1}, {'current': 1, 'ach_id': 362, 'cond_id': 1}, {'current': 1, 'ach_id': 363, 'cond_id': 1}, {'current': 1, 'ach_id': 364, 'cond_id': 1}, {'current': 1, 'ach_id': 365, 'cond_id': 1}, {'current': 1, 'ach_id': 366, 'cond_id': 1}, {'current': 1, 'ach_id': 18, 'cond_id': 1}, {'current': 1, 'ach_id': 20, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=20000)
			self.UpdateEventStatus(event_id=1053)
			self.UpdateEventStatus(event_id=1004)
			self.BuyShopItem(pos_x=20,pos_y=19,island_id=1,item_id=800014)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 22, 'cond_id': 1}, {'current': 1, 'ach_id': 24, 'cond_id': 1}, {'current': 6, 'ach_id': 55, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1005)
			self.UpdateEventStatus(event_id=1054)
			self.legitarena()
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 20008, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 2, 'quest_id': 8}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 68, 'cond_id': 1}, {'current': 2, 'ach_id': 362, 'cond_id': 1}, {'current': 2, 'ach_id': 363, 'cond_id': 1}, {'current': 2, 'ach_id': 364, 'cond_id': 1}, {'current': 2, 'ach_id': 365, 'cond_id': 1}, {'current': 2, 'ach_id': 366, 'cond_id': 1}, {'current': 2, 'ach_id': 18, 'cond_id': 1}, {'current': 2, 'ach_id': 20, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=50062)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 20008, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 3, 'quest_id': 8}])
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 362, 'cond_id': 1}, {'current': 3, 'ach_id': 363, 'cond_id': 1}, {'current': 3, 'ach_id': 364, 'cond_id': 1}, {'current': 3, 'ach_id': 365, 'cond_id': 1}, {'current': 3, 'ach_id': 366, 'cond_id': 1}, {'current': 3, 'ach_id': 18, 'cond_id': 1}, {'current': 3, 'ach_id': 20, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 362, 'cond_id': 1}, {'current': 4, 'ach_id': 363, 'cond_id': 1}, {'current': 4, 'ach_id': 364, 'cond_id': 1}, {'current': 4, 'ach_id': 365, 'cond_id': 1}, {'current': 4, 'ach_id': 366, 'cond_id': 1}, {'current': 4, 'ach_id': 18, 'cond_id': 1}, {'current': 4, 'ach_id': 20, 'cond_id': 1}])
			self.getAllMailF()
			self.refreshtoken()
			maxunit=self.findUnit(19801)['unit_id']
			self.ClaimAchievementReward(target_unit_id=maxunit,activate_quest_list=[{'quest_id': 20009}],ach_id=20008)
			self.UpdateAchievement(ach_list=[{'current': 8, 'ach_id': 21001, 'cond_id': 1}])

			self.feedunit(maxunit,5,skip=False)
			self.feedunit(maxunit,5,skip=False)
			self.feedunit(maxunit,5,skip=False)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 31, 'cond_id': 1}])
			self.UpdateDailyQuest(quests=[{'progressed': 3, 'quest_id': 2}])
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 10001, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 31, 'cond_id': 1}])
			self.ActivateQuests(quests=[{'quest_id': 10002}, {'quest_id': 10003}])
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 31, 'cond_id': 1}])
			self.doMission(region_id=3,difficulty=1,stage_no=1)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 177, 'cond_id': 1}, {'current': 6, 'ach_id': 178, 'cond_id': 1}, {'current': 6, 'ach_id': 179, 'cond_id': 1}, {'current': 6, 'ach_id': 299, 'cond_id': 1}, {'current': 6, 'ach_id': 300, 'cond_id': 1}, {'current': 6, 'ach_id': 303, 'cond_id': 1}, {'current': 6, 'ach_id': 304, 'cond_id': 1}, {'current': 6, 'ach_id': 305, 'cond_id': 1}, {'current': 6, 'ach_id': 498, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=540)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 264, 'cond_id': 1}])
			self.doMission(region_id=3,difficulty=1,stage_no=2)
			self.UpdateEventStatus(event_id=541)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 264, 'cond_id': 1}])
			self.doMission(region_id=3,difficulty=1,stage_no=3)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 264, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=542)
			self.doMission(region_id=3,difficulty=1,stage_no=4)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 264, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=543)
			self.doMission(region_id=3,difficulty=1,stage_no=5)
			self.UpdateEventStatus(event_id=544)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 264, 'cond_id': 1}])
			self.doMission(region_id=3,difficulty=1,stage_no=6)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 264, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=545)
			self.doMission(region_id=3,difficulty=1,stage_no=7)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 96, 'cond_id': 1}, {'current': 1, 'ach_id': 97, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=546)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 264, 'cond_id': 1}, {'current': 1, 'ach_id': 20009, 'cond_id': 1}])
			self.ClaimAchievementReward(ach_id=264)
			self.UpdateEventStatus(event_id=18)
			self.UpdateEventStatus(event_id=20001)
			self.UpdateEventStatus(event_id=8)
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20010}],ach_id=20009)
			self.UpdateAchievement(ach_list=[{'current': 9, 'ach_id': 21001, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1008)
			self.BuyShopItem(pos_x=22,pos_y=13,island_id=1,item_id=800011)
			self.UpdateEventStatus(event_id=1007)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 55, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1055)
			self.UpdateEventStatus(event_id=1024)
			self.doMission(region_id=4,difficulty=1,stage_no=1)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 265, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=512)
			self.doMission(region_id=4,difficulty=1,stage_no=2)
			self.UpdateEventStatus(event_id=513)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 265, 'cond_id': 1}])
			self.feedunit(maxunit,5,skip=False)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 31, 'cond_id': 1}])
			self.feedunit(maxunit,5,skip=False)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 31, 'cond_id': 1}])
			self.doMission(region_id=4,difficulty=1,stage_no=3)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 177, 'cond_id': 1}, {'current': 7, 'ach_id': 178, 'cond_id': 1}, {'current': 7, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 299, 'cond_id': 1}, {'current': 7, 'ach_id': 300, 'cond_id': 1}, {'current': 7, 'ach_id': 303, 'cond_id': 1}, {'current': 7, 'ach_id': 304, 'cond_id': 1}, {'current': 7, 'ach_id': 305, 'cond_id': 1}, {'current': 7, 'ach_id': 498, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=514)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 265, 'cond_id': 1}])
			self.doMission(region_id=4,difficulty=1,stage_no=4)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 265, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=515)
			self.UpdateEventStatus(event_id=60025)
			self.doMission(region_id=4,difficulty=1,stage_no=5)
			self.UpdateEventStatus(event_id=516)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 265, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1010)
			self.BuyShopItem(pos_x=18,pos_y=7,island_id=1,item_id=800010)
			self.UpdateAchievement(ach_list=[{'current': 8, 'ach_id': 55, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1009)
			self.UpdateEventStatus(event_id=1056)
			self.UpdateEventStatus(event_id=10011)
			self.UpdateEventStatus(event_id=60008)
			self.doMission(region_id=4,difficulty=1,stage_no=6)
			self.doDungeon(stage_id=1, dungeon_id=8001)
			self.UpdateAchievement(
				ach_list=[{'current': 1, 'ach_id': 46, 'cond_id': 1}, {'current': 1, 'ach_id': 49, 'cond_id': 1},
						  {'current': 1, 'ach_id': 20010, 'cond_id': 1}, {'current': 1, 'ach_id': 203, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=20002)
			self.UpdateEventStatus(event_id=70004)
			self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 9}])
			self.UpdateAchievement(
				ach_list=[{'current': 1, 'ach_id': 47, 'cond_id': 1}, {'current': 1, 'ach_id': 415, 'cond_id': 1},
						  {'current': 1, 'ach_id': 416, 'cond_id': 1}, {'current': 1, 'ach_id': 417, 'cond_id': 1}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20011}], ach_id=20010)
			self.UpdateAchievement(ach_list=[{'current': 10, 'ach_id': 21001, 'cond_id': 1}])
			self.doDungeon(stage_id=1, dungeon_id=5001)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 48, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=70003)
			self.UpdateDailyQuest(quests=[{'progressed': 1, 'quest_id': 14}])
			self.UpdateAchievement(
				ach_list=[{'current': 2, 'ach_id': 49, 'cond_id': 1}, {'current': 1, 'ach_id': 20011, 'cond_id': 1}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20012}], ach_id=20011)
			self.UpdateAchievement(ach_list=[{'current': 11, 'ach_id': 21001, 'cond_id': 1}])
			self.doMission(region_id=4,difficulty=1,stage_no=7)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 265, 'cond_id': 1}, {'current': 1, 'ach_id': 20012, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=517)
			self.ClaimAchievementReward(ach_id=265)
			self.UpdateEventStatus(event_id=9)
			self.UpdateEventStatus(event_id=10)
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20013}],ach_id=20012)
			self.UpdateAchievement(ach_list=[{'current': 12, 'ach_id': 21001, 'cond_id': 1}])
			self.getAllMailF()
			self.doMission(region_id=5,difficulty=1,stage_no=1)
			self.UpdateAchievement(ach_list=[{'current': 8, 'ach_id': 177, 'cond_id': 1}, {'current': 8, 'ach_id': 178, 'cond_id': 1}, {'current': 8, 'ach_id': 179, 'cond_id': 1}, {'current': 8, 'ach_id': 299, 'cond_id': 1}, {'current': 8, 'ach_id': 300, 'cond_id': 1}, {'current': 8, 'ach_id': 303, 'cond_id': 1}, {'current': 8, 'ach_id': 304, 'cond_id': 1}, {'current': 8, 'ach_id': 305, 'cond_id': 1}, {'current': 8, 'ach_id': 498, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=518)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 266, 'cond_id': 1}])
			self.doMission(region_id=5,difficulty=1,stage_no=2)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 266, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=519)
			self.doMission(region_id=5,difficulty=1,stage_no=3)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 266, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=520)
			self.doMission(region_id=5,difficulty=1,stage_no=4)
			self.UpdateEventStatus(event_id=521)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 266, 'cond_id': 1}])
			self.doMission(region_id=5,difficulty=1,stage_no=5)
			self.UpdateEventStatus(event_id=522)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 266, 'cond_id': 1}])
			self.doMission(region_id=5,difficulty=1,stage_no=6)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 266, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=533)
			self.doDungeon(stage_id=2,dungeon_id=5001)
			for i in range(5):
				self.doDungeon(stage_id=3,dungeon_id=5001)
				self.UpdateAchievement(ach_list=[{'current': i+1, 'ach_id': 20013, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 9, 'ach_id': 177, 'cond_id': 1}, {'current': 9, 'ach_id': 178, 'cond_id': 1}, {'current': 9, 'ach_id': 179, 'cond_id': 1}, {'current': 9, 'ach_id': 299, 'cond_id': 1}, {'current': 9, 'ach_id': 300, 'cond_id': 1}, {'current': 9, 'ach_id': 303, 'cond_id': 1}, {'current': 9, 'ach_id': 304, 'cond_id': 1}, {'current': 9, 'ach_id': 305, 'cond_id': 1}, {'current': 9, 'ach_id': 498, 'cond_id': 1}])
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 49, 'cond_id': 1}])
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20014}],ach_id=20013)
			self.UpdateAchievement(ach_list=[{'current': 13, 'ach_id': 21001, 'cond_id': 1}])
			self.addfriends()
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20015}],ach_id=20014)
			self.doMission(region_id=5, difficulty=1, stage_no=7)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 94, 'cond_id': 1}])
			self.UpdateAchievement(
				ach_list=[{'current': 7, 'ach_id': 266, 'cond_id': 1}, {'current': 1, 'ach_id': 20015, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=523)
			self.ClaimAchievementReward(ach_id=266)
			self.UpdateEventStatus(event_id=12)
			self.UpdateEventStatus(event_id=13)
			self.UpdateEventStatus(event_id=19)
			self.ClaimAchievementReward(activate_quest_list=[{'quest_id': 20016}], ach_id=20015)
			self.UpdateAchievement(ach_list=[{'current': 15, 'ach_id': 21001, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=1)
			self.UpdateEventStatus(event_id=547)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 267, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=60051)
			self.doMission(region_id=6, difficulty=1, stage_no=2)
			self.UpdateEventStatus(event_id=548)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 267, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=3)
			self.UpdateEventStatus(event_id=549)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 267, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=4)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 267, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=550)
			self.UpdateAchievement(
				ach_list=[{'current': 14, 'ach_id': 177, 'cond_id': 1}, {'current': 14, 'ach_id': 178, 'cond_id': 1},
						  {'current': 14, 'ach_id': 179, 'cond_id': 1}, {'current': 14, 'ach_id': 299, 'cond_id': 1},
						  {'current': 14, 'ach_id': 300, 'cond_id': 1}, {'current': 14, 'ach_id': 303, 'cond_id': 1},
						  {'current': 14, 'ach_id': 304, 'cond_id': 1}, {'current': 14, 'ach_id': 305, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=5)
			self.UpdateEventStatus(event_id=551)
			self.UpdateAchievement(ach_list=[{'current': 5, 'ach_id': 267, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=6)
			self.UpdateEventStatus(event_id=552)
			self.UpdateAchievement(ach_list=[{'current': 6, 'ach_id': 267, 'cond_id': 1}])
			self.doMission(region_id=6, difficulty=1, stage_no=7)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 103, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=553)
			self.UpdateAchievement(ach_list=[{'current': 7, 'ach_id': 267, 'cond_id': 1}])
			self.ClaimAchievementReward(ach_id=267)
			self.UpdateEventStatus(event_id=20)
			self.UpdateEventStatus(event_id=21)
			self.UpdateEventStatus(event_id=14)
			self.doMission(region_id=7, difficulty=1, stage_no=1)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 268, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=524)
			self.doMission(region_id=7, difficulty=1, stage_no=2)
			self.UpdateEventStatus(event_id=525)
			self.UpdateAchievement(ach_list=[{'current': 2, 'ach_id': 268, 'cond_id': 1}])
			self.doMission(region_id=7, difficulty=1, stage_no=3)
			self.UpdateEventStatus(event_id=526)
			self.doMission(region_id=7, difficulty=1, stage_no=4)
			self.UpdateEventStatus(event_id=527)
			self.UpdateEventStatus(event_id=50012)
			self.doMission(region_id=7, difficulty=1, stage_no=5)
			self.UpdateEventStatus(event_id=528)
			self.ActivateQuests(quests=[{'quest_id': 10005}])
			self.doMission(region_id=7, difficulty=1, stage_no=6)
			self.UpdateEventStatus(event_id=529)
			self.doMission(region_id=7, difficulty=1, stage_no=7)
			self.UpdateEventStatus(event_id=534)
			self.ClaimAchievementReward(ach_id=268)
			self.UpdateEventStatus(event_id=15)
			self.UpdateEventStatus(event_id=22)
			self.doMission(region_id=8, difficulty=1, stage_no=1)
			self.UpdateEventStatus(event_id=554)
			self.doMission(region_id=8, difficulty=1, stage_no=2)
			self.UpdateEventStatus(event_id=555)
			self.doMission(region_id=8, difficulty=1, stage_no=3)
			self.UpdateEventStatus(event_id=556)
			self.doMission(region_id=8, difficulty=1, stage_no=4)
			self.UpdateEventStatus(event_id=557)
			self.doMission(region_id=8, difficulty=1, stage_no=5)
			self.UpdateEventStatus(event_id=558)
			self.doMission(region_id=8, difficulty=1, stage_no=6)
			self.UpdateEventStatus(event_id=559)
			self.doMission(region_id=8, difficulty=1, stage_no=7)
			self.UpdateEventStatus(event_id=560)
			self.ClaimAchievementReward(ach_id=269)
			self.UpdateEventStatus(event_id=23)
			self.UpdateEventStatus(event_id=24)
			self.doMission(region_id=9, difficulty=1, stage_no=1)
			self.UpdateEventStatus(event_id=561)
			self.UpdateEventStatus(event_id=70002)
			self.doMission(region_id=9, difficulty=1, stage_no=2)
			self.UpdateEventStatus(event_id=562)
			self.doMission(region_id=9, difficulty=1, stage_no=3)
			self.UpdateEventStatus(event_id=563)
			self.UpdateAchievement(
				ach_list=[{'current': 7, 'ach_id': 268, 'cond_id': 1}, {'current': 7, 'ach_id': 269, 'cond_id': 1},
						  {'current': 10, 'ach_id': 498, 'cond_id': 1}])
			self.ClaimAchievementReward(ach_id=268)
			self.ClaimAchievementReward(ach_id=269)
			self.UpdateEventStatus(event_id=60050)
			self.TriggerShopItem(trigger_id=320)
			self.GetShopInfo()
			self.UpdateEventStatus(event_id=70006)
			self.UpdateEventStatus(event_id=70007)
			self.UpdateEventStatus(event_id=70008)

			self.UpdateEventStatus(event_id=1033)
			self.BuyShopItem(pos_x=6, pos_y=14, island_id=1, item_id=800009)
			self.UpdateAchievement(ach_list=[{'current': 9, 'ach_id': 55, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1034)
			self.UpdateEventStatus(event_id=1030)
			self.BuyShopItem(pos_x=14, pos_y=8, island_id=1, item_id=900010)
			self.UpdateEventStatus(event_id=1031)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 144, 'cond_id': 1}])
			self.UpdateAchievement(
				ach_list=[{'current': 1, 'ach_id': 143, 'cond_id': 1}, {'current': 1, 'ach_id': 145, 'cond_id': 1},
						  {'current': 10, 'ach_id': 55, 'cond_id': 1}])
			self.UpdateEventStatus(event_id=1035)
			self.UpdateEventStatus(event_id=1032)
			self.UpdateEventStatus(event_id=1020)
			self.BuyIsland(island_id=2)
			self.UpdateEventStatus(event_id=1019)
			self.BuyIsland(island_id=3)
			self.UpdateAchievement(ach_list=[{'current': 1, 'ach_id': 54, 'cond_id': 1}])
			self.BuyShopItem(pos_x=18, pos_y=19, island_id=1, item_id=800014)
			self.UpdateAchievement(
				ach_list=[{'current': 2, 'ach_id': 22, 'cond_id': 1}, {'current': 2, 'ach_id': 24, 'cond_id': 1}])
			self.BuyShopItem(pos_x=16, pos_y=19, island_id=1, item_id=800014)
			self.UpdateAchievement(ach_list=[{'current': 3, 'ach_id': 24, 'cond_id': 1}])
			self.BuyShopItem(pos_x=14, pos_y=19, island_id=1, item_id=800014)
			self.UpdateAchievement(ach_list=[{'current': 4, 'ach_id': 24, 'cond_id': 1}])

	def bind(self,q):
		username=Tools().rndUser().lower()
		mail='%s@gmail.com'%(username)
		password=Tools().rndPw(9)
		print mail,username,password
		self.id=username
		self.email=mail

		q.useold()
		did=q.signup_proc(username,mail,password)
		q.bind(username,password)
		candidate_uid=int(q.uid)
		self.CheckCandidateUid(candidate_uid=candidate_uid)
		q.bind(username,password,True)
		self.sessionkey=q.sessionkey
		self.ProcessGuestTransition(candidate_uid=candidate_uid,sessionkey=self.sessionkey)
		#self.HubUserLogin()

if __name__ == "__main__":
	uid,did=QPYOU().createNew()
	a=API(uid,did)
	a.setRegion('eu')
	a.setIDFA(Tools().rndDeviceId())
	a.completeTutorial()
	#a.getServerStatus()
	#a.getVersionInfo()
	#a.CheckLoginBlock()
	#a.login()