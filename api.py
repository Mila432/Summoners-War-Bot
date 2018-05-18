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

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self,uid,did,id=None,email=None,session=None):
		self.crypter=Crypter()
		self.s=requests.session()
		self.s.verify=False
		self.s.headers.update({'User-Agent':'Summoners%20War/3.8.5.38500 CFNetwork/808.2.16 Darwin/16.3.0'})
		#if 'Admin-PC' == socket.gethostname():
		#	self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})
		self.game_index=2623
		self.proto_ver=11120
		self.app_version='3.8.5'
		self.c2_api='http://summonerswar-%s.qpyou.cn/api/gateway_c2.php'
		self.uid=int(uid)
		self.did=int(did)
		self.isHive=False
		if id and email:
			self.log('hive account')
			self.id=id
			self.email=email
			self.isHive=True
			self.session_key=session
		self.log('uid:%s did:%s'%(uid,did))

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
			self.region=random.choice(regions)
		self.region=region
		self.c2_api=self.c2_api%(self.region)
		
	def setIDFA(self,id):
		self.idfa=id
		
	def log(self,msg):
		print '[%s]:%s'%(time.strftime('%H:%M:%S'),msg)
		
	def callAPI(self,path,data,repeat=False):
		try:
			old_data=None
			if not repeat:
				if type(data)<>str:
					old_data=data
					data=json.dumps(data, indent=1).replace(' ','	').replace(',	',',')
				data=self.crypter.encrypt_request(data,2 if '_c2.php' in path else 1)
			ts=int(time.time())
			try:
				res=self.s.post(path,data,headers={'SmonTmVal':str(old_data)['ts_val'] if old_data else str(self.crypter.GetPlayerServerConnectElapsedTime(ts)),'SmonChecker':self.crypter.getSmonChecker(data,ts)})
			except:
				return self.callAPI(path,data,True)
			res= self.crypter.decrypt_response(res.content,2 if '_c2.php' in path else 1)
			if 'wizard_info' in res and 'wizard_id' in res:
				self.updateWizard(json.loads(res)['wizard_info'])
			rj=json.loads(res)
			if 'ret_code' in res:
				if rj['ret_code']<>0:
					self.log('failed to send data for %s'%(rj['command']))
					return None
				#self.log('ret_code:%s command:%s'%(rj['ret_code'],rj['command']))
			return rj
		except:
			return self.callAPI(path,data,True)

	def getServerStatus(self):
		data={}
		data['game_index']=self.game_index
		data['proto_ver']=self.proto_ver
		data['channel_uid']=0
		return self.callAPI('http://summonerswar-eu.qpyou.cn/api/server_status_c2.php',data)

	def getVersionInfo(self):
		data={}
		data['game_index']=self.game_index
		data['proto_ver']=self.proto_ver
		data['channel_uid']=0
		res= self.callAPI('http://summonerswar-eu.qpyou.cn/api/version_info_c2.php',data)
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
			data=OrderedDict([('command',cmd),('game_index',self.game_index),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid)])
		elif kind ==2:
			data=OrderedDict([('command',cmd),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.uid),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime())])
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

	def GetArenaLog(self):
		data=self.base_data('GetArenaLog',2)
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

	def SetWizardName(self,name):
		self.log('new name:%s'%(name))
		data=OrderedDict([('command','SetWizardName'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('wizard_name',name)])
		return self.callAPI(self.c2_api,data)

	def UpdateEventStatus(self,event_id):
		data=OrderedDict([('command','UpdateEventStatus'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('event_id',event_id)])
		return self.callAPI(self.c2_api,data)

	def GetEventTimeTable(self):
		data=OrderedDict([('command','GetEventTimeTable'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('lang','1'),('app_version',self.app_version)])
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
		if self.isHive:
			return str(self.session_key)
		else:
			return str(self.uid)
		
	def BattleScenarioStart(self,region_id,stage_no,difficulty,unit_id_list,mentor_helper_list=None):
		data=OrderedDict([('command','BattleScenarioStart'),('wizard_id',self.wizard_id),('session_key',str(self.getUID())),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('region_id',region_id),('stage_no',stage_no),('difficulty',difficulty),('unit_id_list',unit_id_list),('helper_list',[]),('mentor_helper_list',[] if not mentor_helper_list else mentor_helper_list),('npc_friend_helper_list',[]),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleArenaStart(self,opp_wizard_id,unit_id_list):
		data=OrderedDict([('command','BattleArenaStart'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('opp_wizard_id',opp_wizard_id),('unit_id_list',unit_id_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleDungeonStart(self,dungeon_id,stage_id,unit_id_list):
		data=OrderedDict([('command','BattleDungeonStart'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('dungeon_id',dungeon_id),('stage_id',stage_id),('helper_list',[]),('mentor_helper_list',[]),('npc_friend_helper_list',[]),('unit_id_list',unit_id_list),('cash_used','0'),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleTrialTowerStart_v2(self,difficulty,floor_id,unit_id_list):
		data=OrderedDict([('command','BattleTrialTowerStart_v2'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('difficulty',difficulty),('floor_id',floor_id),('unit_id_list',unit_id_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleScenarioResult(self,battle_key,opp_unit_status_list,unit_id_list,position):
		data=OrderedDict([('command','BattleScenarioResult'),('wizard_id',self.wizard_id),('session_key',str(self.getUID())),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('win_lose',1),('opp_unit_status_list',opp_unit_status_list),('unit_id_list',unit_id_list),('position',position),('clear_time',31086),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleArenaResult(self,battle_key,opp_unit_status_list,unit_id_list):
		data=OrderedDict([('command','BattleArenaResult'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('win_lose',1),('opp_unit_status_list',opp_unit_status_list),('unit_id_list',unit_id_list),('retry',0)])
		return self.callAPI(self.c2_api,data)

	def BattleDungeonResult(self,battle_key,dungeon_id,stage_id,unit_id_list,opp_unit_status_list):
		data=OrderedDict([('command','BattleDungeonResult'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('battle_key',battle_key),('dungeon_id',dungeon_id),('stage_id',stage_id),('win_lose',1),('unit_id_list',unit_id_list),('opp_unit_status_list',opp_unit_status_list),('retry',0)])
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
		return self.callAPI(self.c2_api,data)

	def EquipRune(self,rune_id,unit_id):
		data=OrderedDict([('command','EquipRune'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('rune_id',rune_id),('unit_id',unit_id)])
		return self.callAPI(self.c2_api,data)

	def UpgradeRune(self,rune_id,upgrade_curr,cash_used=0,stone_used=0):
		data=OrderedDict([('command','UpgradeRune'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('rune_id',rune_id),('upgrade_curr',upgrade_curr),('cash_used',cash_used),('stone_used',stone_used)])
		return self.callAPI(self.c2_api,data)

	def BuyShopItem(self,item_id,island_id,pos_x,pos_y):
		data=OrderedDict([('command','BuyShopItem'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('item_id',item_id),('island_id',island_id),('pos_x',pos_x),('pos_y',pos_y)])
		return self.callAPI(self.c2_api,data)

	def ClaimAchievementReward(self,ach_id):
		data=OrderedDict([('command','ClaimAchievementReward'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('ach_id',ach_id)])
		return self.callAPI(self.c2_api,data)

	def RewardDailyQuest(self,quest_id):
		data=OrderedDict([('command','RewardDailyQuest'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('quest_id',quest_id)])
		return self.callAPI(self.c2_api,data)

	def SacrificeUnit(self,target_id,source_list):
		data=OrderedDict([('command','SacrificeUnit'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('target_id',target_id),('island_id','1'),('building_id','0'),('pos_x','8'),('pos_y','14'),('source_list',source_list)])
		return self.callAPI(self.c2_api,data)

	def UpgradeUnit(self,target_id,source_list):
		data=OrderedDict([('command','UpgradeUnit'),('wizard_id',self.wizard_id),('session_key',self.getUID()),('proto_ver',self.proto_ver),('infocsv',self.infocsv),('channel_uid',self.uid),('ts_val',self.crypter.GetPlayerServerConnectElapsedTime()),('target_id',target_id),('island_id','1'),('building_id','0'),('pos_x','10'),('pos_y','19'),('source_list',source_list)])
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
		self.user=input
		self.wizard_id=input['wizard_info']['wizard_id']
		self.log('wizard_id:%s'%(self.wizard_id))
	
	def updateWizard(self,input):
		if hasattr(self, 'user'):
			self.user['wizard_info']=input
			self.log(self.getUserInfo())
	
	def getUserInfo(self):
		#return 'id:%s username:%s energy:%s mana:%s crystal:%s level:%s'%(self.user['wizard_info']['wizard_id'],self.user['wizard_info']['wizard_name'],self.user['wizard_info']['wizard_energy'],self.user['wizard_info']['wizard_mana'],self.user['wizard_info']['wizard_crystal'],self.user['wizard_info']['wizard_level'])
		return 'username:%s energy:%s mana:%s crystal:%s level:%s'%(self.user['wizard_info']['wizard_name'],self.user['wizard_info']['wizard_energy'],self.user['wizard_info']['wizard_mana'],self.user['wizard_info']['wizard_crystal'],self.user['wizard_info']['wizard_level'])
		
	def GuestLogin(self):
		data=OrderedDict([('command','GuestLogin'),('game_index',self.game_index),('proto_ver',self.proto_ver),('app_version',self.app_version),('infocsv',self.infocsv),('uid',self.uid),('channel_uid',self.uid),('did',self.did),('push',1),('is_emulator',0),('country','DE'),('lang','eng'),('lang_game',1),('mac_address','02:00:00:00:00:00'),('device_name','iPhone10,6'),('os_version','11.1'),('token','0000000000000000000000000000000000000000000000000000000000000000'),('idfv',self.idfa),('adid','00000000-0000-0000-0000-000000000000'),('binary_size',0),('binary_check',''),('create_if_not_exist',1)])
		res= self.callAPI(self.c2_api,data)
		self.setUser(res)
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
		#self.ReceiveDailyRewardSpecial()
		return res
		
	def HubUserLogin(self):
		data=OrderedDict([('command','HubUserLogin'),('game_index',self.game_index),('proto_ver',self.proto_ver),('app_version',self.app_version),('session_key',self.session_key),('infocsv',self.infocsv),('uid',self.uid),('channel_uid',self.uid),('did',self.did),('id',self.id),('email',self.email),('push',1),('is_emulator',0),('country','RU'),('lang','eng'),('lang_game',1),('mac_address','02:00:00:00:00:00'),('device_name','iPhone10,6'),('os_version','11.1'),('token','0000000000000000000000000000000000000000000000000000000000000000'),('idfv',self.idfa),('adid','00000000-0000-0000-0000-000000000000'),('binary_size',0),('binary_check',''),('create_if_not_exist',0)])
		res= self.callAPI(self.c2_api,data)
		self.setUser(res)
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
		
	def doMission(self,region_id,stage_no,difficulty,exp=False):
		unit_id_list=[]
		for unit in self.user['defense_unit_list']:
			if len(unit_id_list)<=4:
				unit_id_list.append({'unit_id':unit['unit_id']})
		if len(unit_id_list)==0:
			print 'units missing'
			exit(1)
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
		return battle_end

	def removeAllObstacle(self):
		for obstacle in self.user['obstacle_list']:
			self.CleanObstacle(obstacle['obstacle_id'])
		
	def doArena(self,opp_wizard_id):
		unit_id_list=[]
		for unit in self.user['defense_unit_list']:
			if len(unit_id_list)<4:
				unit_id_list.append({'unit_id':unit['unit_id']})
		battle_start=self.BattleArenaStart(opp_wizard_id,unit_id_list)
		if not battle_start:
			self.log('dont have battle data')
			return
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,1)
		battle_end=self.BattleArenaResult(battle_key,opp_unit_status_list,unit_id_list)
		if battle_end:
			self.parseBattleResult(battle_end,opp_wizard_id)
		return battle_end

	def doDungeon(self,dungeon_id,stage_id):
		unit_id_list=[]
		for unit in self.user['defense_unit_list']:
			if len(unit_id_list)<5:
				unit_id_list.append({'unit_id':unit['unit_id']})
		if hasattr(self,'refillEnergy') and self.user['wizard_info']['wizard_crystal']>=30 and self.user['wizard_info']['wizard_energy']<=8:
			self.BuyShopItem('100001',0,0,0)
		battle_start=self.BattleDungeonStart(dungeon_id,stage_id,unit_id_list)
		if not battle_start:
			self.log('dont have battle data')
			return
		battle_key,opp_unit_status_list=self.parseBattleStart(battle_start,2)
		battle_end=self.BattleDungeonResult(battle_key,dungeon_id,stage_id,unit_id_list,opp_unit_status_list)
		if battle_end:
			self.parseBattleResult(battle_end,'%s:%s'%(dungeon_id,stage_id))
		return battle_end

	def doTower(self,floor_id,difficulty):
		unit_id_list=[]
		for unit in self.user['defense_unit_list']:
			if len(unit_id_list)<5:
				unit_id_list.append({'unit_id':unit['unit_id']})
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

	def level2(self):
		self.UpdateAchievement([{'current': 7, 'ach_id': 269, 'cond_id': 1}])
		self.ClaimAchievementReward(269)
		self.getAllMail()
		
	def level3(self):
		quest_list=self.GetDailyQuests()['quest_list']
		for quest in quest_list:
			if quest['completed']==1 and quest['rewarded']==0: 
				self.RewardDailyQuest(quest['quest_id'])
		self.UpdateAchievement([{'current': 7, 'ach_id': 263, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 450, 'ach_id': 4, 'cond_id': 1}, {'current': 2, 'ach_id': 23, 'cond_id': 1}, {'current': 9, 'ach_id': 29, 'cond_id': 1}, {'current': 1, 'ach_id': 171, 'cond_id': 1}, {'current': 1, 'ach_id': 205, 'cond_id': 1}, {'current': 1, 'ach_id': 206, 'cond_id': 1}, {'current': 1, 'ach_id': 213, 'cond_id': 1}, {'current': 1, 'ach_id': 214, 'cond_id': 1}, {'current': 1, 'ach_id': 229, 'cond_id': 1}, {'current': 1, 'ach_id': 230, 'cond_id': 1}, {'current': 1, 'ach_id': 260, 'cond_id': 1}, {'current': 1, 'ach_id': 261, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 177, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 178, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 179, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 299, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 300, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 303, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 304, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 3, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 0, 'ach_id': 171, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 2, 'ach_id': 6, 'cond_id': 2}, {'current': 1, 'ach_id': 33, 'cond_id': 2}, {'current': 5, 'ach_id': 177, 'cond_id': 1}, {'current': 5, 'ach_id': 178, 'cond_id': 1}, {'current': 5, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 257, 'cond_id': 1}, {'current': 5, 'ach_id': 299, 'cond_id': 1}, {'current': 5, 'ach_id': 300, 'cond_id': 1}, {'current': 5, 'ach_id': 303, 'cond_id': 1}, {'current': 5, 'ach_id': 304, 'cond_id': 1}, {'current': 5, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 2, 'ach_id': 6, 'cond_id': 3}, {'current': 7, 'ach_id': 264, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 6, 'ach_id': 177, 'cond_id': 1}, {'current': 6, 'ach_id': 178, 'cond_id': 1}, {'current': 6, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 265, 'cond_id': 1}, {'current': 6, 'ach_id': 299, 'cond_id': 1}, {'current': 6, 'ach_id': 300, 'cond_id': 1}, {'current': 6, 'ach_id': 303, 'cond_id': 1}, {'current': 6, 'ach_id': 304, 'cond_id': 1}, {'current': 6, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 2, 'ach_id': 6, 'cond_id': 1}, {'current': 7, 'ach_id': 177, 'cond_id': 1}, {'current': 7, 'ach_id': 178, 'cond_id': 1}, {'current': 7, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 266, 'cond_id': 1}, {'current': 7, 'ach_id': 299, 'cond_id': 1}, {'current': 7, 'ach_id': 300, 'cond_id': 1}, {'current': 7, 'ach_id': 303, 'cond_id': 1}, {'current': 7, 'ach_id': 304, 'cond_id': 1}, {'current': 7, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 7, 'ach_id': 267, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 8, 'ach_id': 177, 'cond_id': 1}, {'current': 8, 'ach_id': 178, 'cond_id': 1}, {'current': 8, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 268, 'cond_id': 1}, {'current': 8, 'ach_id': 299, 'cond_id': 1}, {'current': 8, 'ach_id': 300, 'cond_id': 1}, {'current': 8, 'ach_id': 303, 'cond_id': 1}, {'current': 8, 'ach_id': 304, 'cond_id': 1}, {'current': 8, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 7, 'ach_id': 269, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 1, 'ach_id': 33, 'cond_id': 3}, {'current': 9, 'ach_id': 177, 'cond_id': 1}, {'current': 9, 'ach_id': 178, 'cond_id': 1}, {'current': 9, 'ach_id': 179, 'cond_id': 1}, {'current': 9, 'ach_id': 299, 'cond_id': 1}, {'current': 9, 'ach_id': 300, 'cond_id': 1}, {'current': 9, 'ach_id': 303, 'cond_id': 1}, {'current': 9, 'ach_id': 304, 'cond_id': 1}, {'current': 9, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 7, 'ach_id': 270, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 7, 'ach_id': 271, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 1, 'ach_id': 5, 'cond_id': 1}, {'current': 10, 'ach_id': 29, 'cond_id': 1}, {'current': 1, 'ach_id': 192, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 10, 'ach_id': 177, 'cond_id': 1}, {'current': 10, 'ach_id': 178, 'cond_id': 1}, {'current': 10, 'ach_id': 179, 'cond_id': 1}, {'current': 7, 'ach_id': 272, 'cond_id': 1}, {'current': 10, 'ach_id': 299, 'cond_id': 1}, {'current': 10, 'ach_id': 300, 'cond_id': 1}, {'current': 10, 'ach_id': 303, 'cond_id': 1}, {'current': 10, 'ach_id': 304, 'cond_id': 1}, {'current': 10, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 7, 'ach_id': 273, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 13, 'ach_id': 177, 'cond_id': 1}, {'current': 13, 'ach_id': 178, 'cond_id': 1}, {'current': 13, 'ach_id': 179, 'cond_id': 1}, {'current': 13, 'ach_id': 299, 'cond_id': 1}, {'current': 13, 'ach_id': 300, 'cond_id': 1}, {'current': 13, 'ach_id': 303, 'cond_id': 1}, {'current': 13, 'ach_id': 304, 'cond_id': 1}, {'current': 13, 'ach_id': 305, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 2, 'ach_id': 171, 'cond_id': 1}])
		self.UpdateAchievement([{'current': 657, 'ach_id': 4, 'cond_id': 1}])
		self.ClaimAchievementReward(269)
		self.ClaimAchievementReward(1)
		self.ClaimAchievementReward(2)
		self.ClaimAchievementReward(5)
		self.ClaimAchievementReward(33)
		self.ClaimAchievementReward(6)
		self.ClaimAchievementReward(13)
		self.ClaimAchievementReward(15)
		self.ClaimAchievementReward(264)
		self.ClaimAchievementReward(192)
		self.ClaimAchievementReward(263)
		self.ClaimAchievementReward(257)
		self.ClaimAchievementReward(265)
		self.ClaimAchievementReward(266)
		self.ClaimAchievementReward(271)
		self.ClaimAchievementReward(272)
		self.ClaimAchievementReward(267)
		self.ClaimAchievementReward(268)
		self.ClaimAchievementReward(270)
		self.ClaimAchievementReward(273)
		self.getAllMail()

	def level8(self):
		self.UpdateEventStatus(501)
		self.UpdateEventStatus(502)
		self.UpdateEventStatus(503)
		self.UpdateEventStatus(504)
		self.UpdateEventStatus(530)
		self.UpdateEventStatus(3)
		self.UpdateEventStatus(505)
		self.UpdateEventStatus(5)
		self.UpdateEventStatus(60018)
		self.UpdateEventStatus(80001)
		self.UpdateEventStatus(4)
		self.UpdateEventStatus(10001)
		self.UpdateEventStatus(506)
		self.UpdateEventStatus(507)
		self.UpdateEventStatus(508)
		self.UpdateEventStatus(509)
		self.UpdateEventStatus(510)
		self.UpdateEventStatus(531)
		self.UpdateEventStatus(6)
		self.UpdateEventStatus(511)
		self.UpdateEventStatus(60005)
		self.UpdateEventStatus(17)
		self.UpdateEventStatus(541)
		self.UpdateEventStatus(540)
		self.UpdateEventStatus(542)
		self.UpdateEventStatus(543)
		self.UpdateEventStatus(544)
		self.UpdateEventStatus(545)
		self.UpdateEventStatus(18)
		self.UpdateEventStatus(546)
		self.UpdateEventStatus(8)
		self.UpdateEventStatus(20001)
		self.UpdateEventStatus(50029)
		self.UpdateEventStatus(512)
		self.UpdateEventStatus(513)
		self.UpdateEventStatus(514)
		self.UpdateEventStatus(515)
		self.UpdateEventStatus(516)
		self.UpdateEventStatus(532)
		self.UpdateEventStatus(9)
		self.UpdateEventStatus(517)
		self.UpdateEventStatus(10)
		self.UpdateEventStatus(1008)
		self.UpdateEventStatus(518)
		self.UpdateEventStatus(519)
		self.UpdateEventStatus(520)
		self.UpdateEventStatus(521)
		self.UpdateEventStatus(522)
		self.UpdateEventStatus(533)
		self.UpdateEventStatus(523)
		self.UpdateEventStatus(12)
		self.UpdateEventStatus(547)
		self.UpdateEventStatus(548)
		self.UpdateEventStatus(549)
		self.UpdateEventStatus(550)
		self.UpdateEventStatus(551)
		self.UpdateEventStatus(552)
		self.UpdateEventStatus(20)
		self.UpdateEventStatus(553)
		self.UpdateEventStatus(13)
		self.UpdateEventStatus(19)
		self.UpdateEventStatus(21)
		self.UpdateEventStatus(14)
		self.UpdateEventStatus(1010)
		self.UpdateEventStatus(524)
		self.UpdateEventStatus(525)
		self.UpdateEventStatus(526)
		self.UpdateEventStatus(527)
		self.UpdateEventStatus(528)
		self.UpdateEventStatus(529)
		self.UpdateEventStatus(534)
		self.UpdateEventStatus(15)
		self.UpdateEventStatus(70001)
		self.UpdateEventStatus(70005)
		self.UpdateEventStatus(22)
		self.UpdateEventStatus(1020)
		self.UpdateEventStatus(554)
		self.UpdateEventStatus(555)
		self.UpdateEventStatus(556)
		self.UpdateEventStatus(557)
		self.UpdateEventStatus(558)
		self.UpdateEventStatus(559)
		self.UpdateEventStatus(23)
		self.UpdateEventStatus(560)
		self.UpdateEventStatus(24)
		self.UpdateEventStatus(562)
		self.UpdateEventStatus(561)
		self.UpdateEventStatus(563)
		self.UpdateEventStatus(564)
		self.UpdateEventStatus(565)
		self.UpdateEventStatus(566)
		self.UpdateEventStatus(567)
		self.UpdateEventStatus(25)
		self.UpdateEventStatus(568)
		self.UpdateEventStatus(569)
		self.UpdateEventStatus(570)
		self.UpdateEventStatus(571)
		self.UpdateEventStatus(572)
		self.UpdateEventStatus(573)
		self.UpdateEventStatus(574)
		self.UpdateEventStatus(28)
		self.UpdateEventStatus(26)
		self.UpdateEventStatus(27)
		self.UpdateEventStatus(29)
		self.UpdateEventStatus(1030)
		self.UpdateEventStatus(575)
		self.UpdateEventStatus(576)
		self.UpdateEventStatus(577)
		self.UpdateEventStatus(578)
		self.UpdateEventStatus(579)
		self.UpdateEventStatus(580)
		self.UpdateEventStatus(581)
		self.UpdateEventStatus(30)
		self.UpdateEventStatus(31)
		self.UpdateEventStatus(1026)
		self.UpdateEventStatus(1024)
		self.UpdateEventStatus(582)
		self.UpdateEventStatus(583)
		self.UpdateEventStatus(584)
		self.UpdateEventStatus(585)
		self.UpdateEventStatus(586)
		self.UpdateEventStatus(587)
		self.UpdateEventStatus(588)
		self.UpdateEventStatus(32)
		self.UpdateEventStatus(60006)
		self.UpdateEventStatus(60025)
		self.UpdateEventStatus(33)
		self.UpdateEventStatus(1033)
		self.UpdateEventStatus(10017)
		self.UpdateEventStatus(589)
		self.UpdateEventStatus(590)
		self.UpdateEventStatus(591)
		self.UpdateEventStatus(592)
		self.UpdateEventStatus(593)
		self.UpdateEventStatus(594)
		self.UpdateEventStatus(595)
		self.UpdateEventStatus(34)
		self.UpdateEventStatus(34)
		self.UpdateEventStatus(35)
		self.UpdateEventStatus(36)
		self.UpdateEventStatus(50038)
		self.UpdateEventStatus(10019)
		self.UpdateEventStatus(50015)

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

	def completeRegion(self,region,diff=1,skip=0):
		for i in range(7):
			if (i+1)<=skip:
				continue
			self.doMission(region,i+1,diff)
			self.checkArena()

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
		
	def testLogin1(self):
		self.getServerStatus()
		self.getVersionInfo()
		self.CheckLoginBlock()
		self.GuestLogin()
		self.GetDailyQuests()
		self.GetDailyQuests()
		self.GetMiscReward()
		self.GetMailList()
		self.GetArenaLog()
		self.ReceiveDailyRewardSpecial()
		self.receiveDailyRewardInactive()
		self.GetCostumeCollectionList()
		self.CheckDarkPortalStatus()
		self.GetFriendRequest()
		self.GetRTPvPInfo_v3()
		self.getUnitUpgradeRewardInfo()
		self.GetChatServerInfo()
		self.getRtpvpRejoinInfo()
		self.GetEventTimeTable()
		self.GetNoticeDungeon()
		self.GetNoticeChat()
		self.CheckDailyReward()

	def completeTutorial(self):
		if hasattr(self,'user'):
			if self.user['wizard_info']['wizard_mana']<>13000:
				return
		self.getServerStatus()
		self.getVersionInfo()
		self.CheckLoginBlock()
		self.login()#1
		self.GetDailyQuests()#2
		self.GetMiscReward()#3
		self.GetMailList()#4
		self.GetArenaLog()#5
		self.ReceiveDailyRewardSpecial()#6
		self.GetFriendRequest()#7
		self.GetChatServerInfo()#8
		self.getRtpvpRejoinInfo()#9
		self.SetWizardName((Tools().rndHex(9)))#10
		self.UpdateEventStatus(1500)#11
		self.GetEventTimeTable()#12
		self.GetNoticeDungeon()#13
		self.GetNoticeChat()#14
		for building in self.user['building_list']:
			if 'harvest_max' in building:
				building_id=building['building_id']
		self.Harvest(building_id)#15
		self.UpdateEventStatus(60021)#16
		self.TriggerShopItem(20)#17
		self.UpdateEventStatus(1085)#18
		for building in self.user['building_list']:
			if building['building_master_id'] ==2:
				building_id=building['building_id']
		second_unit=self.SummonUnit(building_id,1,[{"island_id":1,"pos_x":7,"pos_y":7,"unit_master_id":10602}])#19
		second_unit=second_unit['unit_list'][0]['unit_id']
		self.UpdateEventStatus(1501)#20
		self.UpdateAchievement([{"ach_id":2,"cond_id":2,"current":1}])#21
		self.UpdateAchievement([{"ach_id":15,"cond_id":2,"current":1}])#22
		defense_unit_list=self.SummonUnit(building_id,2,[{"island_id":1,"pos_x":27,"pos_y":18,"unit_master_id":10101}])#23
		self.UpdateAchievement([{"ach_id":2,"cond_id":1,"current":1},{"ach_id":15,"cond_id":1,"current":1},{"ach_id":33,"cond_id":1,"current":1}])#24
		self.UpdateDailyQuest([{"quest_id":3,"progressed":1}])#25
		self.UpdateEventStatus(1502)#26
		unit_id_list=[]
		first_unit=defense_unit_list['unit_list'][0]['unit_id']
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id']})
		unit_id_list.sort()
		battle_start=self.BattleScenarioStart(1,1,1,unit_id_list)#27
		res=self.parseBattleStart(battle_start)
		self.UpdateDailyQuest([{"quest_id":1,"progressed":3}])#28
		self.UpdateEventStatus(50001)#29
		self.UpdateAchievement([{"ach_id":3,"cond_id":1,"current":1}])
		self.UpdateAchievement([{"ach_id":3,"cond_id":2,"current":1}])
		self.UpdateEventStatus(50035)
		unit_id_list=[]
		pos=0
		for unit in defense_unit_list['defense_unit_list']:
			unit_id_list.append({'unit_id':unit['unit_id'],'pos_id':pos})
			pos+=1
		battle_end=self.BattleScenarioResult(res[0],res[1],unit_id_list,{"island_id":1,"pos_x":14,"pos_y":24})
		self.parseBattleResult(battle_end)
		self.UpdateEventStatus(1503)
		self.UpdateEventStatus(1504)
		self.GetEventTimeTable()#36
		self.SummonUnit(building_id,1,[{"island_id":1,"pos_x":27,"pos_y":18,"unit_master_id":15203}])#37
		self.UpdateAchievement([{"ach_id":2,"cond_id":3,"current":1},{"ach_id":15,"cond_id":3,"current":1}])
		self.UpdateDailyQuest([{"quest_id":3,"progressed":2}])
		self.UpdateEventStatus(1506)
		self.UpdateEventStatus(1507)#41
		for rune in self.user['runes']:
			rune_id=rune['rune_id']
		self.EquipRune(rune_id,first_unit)
		self.UpgradeRune(rune_id,0,0,0)
		self.UpdateDailyQuest([{"quest_id":4,"progressed":1}])
		self.BuyShopItem('800020',1,21,20)#45
		self.UpdateEventStatus(1508)
		self.UpdateEventStatus(1509)
		self.SacrificeUnit(second_unit,[{"source_id":0}])
		self.UpdateAchievement([{"ach_id":13,"cond_id":1,"current":1}])
		self.UpdateAchievement([{"ach_id":31,"cond_id":1,"current":1}])
		self.UpdateDailyQuest([{"quest_id":2,"progressed":1}])
		self.UpdateEventStatus(1510)
		self.UpdateAchievement([{"ach_id":1,"cond_id":1,"current":1}])
		self.UpdateEventStatus(2)
		self.UpdateAchievement([{"ach_id":6,"cond_id":1,"current":1},{"ach_id":6,"cond_id":2,"current":1},{"ach_id":6,"cond_id":3,"current":1}])
		self.UpdateAchievement([{"ach_id":263,"cond_id":1,"current":1}])

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