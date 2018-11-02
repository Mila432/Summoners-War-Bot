from api import API
from qpyou import QPYOU
from tools import Tools

uid,did=QPYOU('236145030').createNew()
a=API(uid,did)
a.setRegion('eu')
a.setIDFA(Tools().rndDeviceId())
a.getServerStatus()
a.getVersionInfo()
a.CheckLoginBlock()
a.login()
a.doMission(1,1,1)#garen forest outskirts
a.doMission(1,2,1)#garen forest south
a.doMission(1,3,1)#garen forest east
a.doMission(1,4,1)#garen forest paths
