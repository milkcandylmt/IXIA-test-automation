#coding=utf8
import base64
import requests
import json
import demjson
import re
import urllib
from copy import deepcopy
import inspect
import time

def get_current_function_name():
    return inspect.stack()[1][3]
# class Product(object):
    # def __init__(self,product="ECOS",user="admin",pwd="admin",dutip="192.168.0.1"):
        # obj_str=product+"_Cfg"
        # print obj_str
        # obj=obj_str(user="admin",pwd="admin",dutip="192.168.0.1")
        # obj=obj_str()
        # return obj
        # cls=getattr(obj,)
        # config_obj=cls()
        # config_obj.setarg(**args)
class WEB_Cfg(object):
    pass
# Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Accept-Encoding:gzip,deflate,sdch
# Accept-Language:zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4
# Connection:keep-alive
# Cookie:jxtd_IP-COM_user=admin|0
# Host:192.168.0.254
# Referer:http://192.168.0.254/cgi/login?username=admin&password=admin
# User-Agent:Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36


# GET /cgi/login?username=admin&password=admin HTTP/1.1
# Host: 192.168.0.254
# Connection: keep-alive
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36
# Referer: http://192.168.0.254/login.htm
# Accept-Encoding: gzip,deflate,sdch
# Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4
# Cookie: jxtd_IP-COM_user=admin|0

#set port
# GET /cgi/set_port?rand=0.5541208076756448&opt=1&port=1&autocfg=0&state=0&priority=0&flowcfg=0&broadcast=3&isolation=0&jumbocfg=1518 HTTP/1.1
# Host: 192.168.0.254
# Connection: keep-alive
# User-Agent: Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36
# Content-Type: application/x-www-form-urlencoded
# Accept: */*
# Referer: http://192.168.0.254/port_config.htm?itm={port:1,linkstatus:4,state:1,priority:0,autocfg:0,flowcfg:0,broadcast:3,isolation:0,jumbo:1518,}&vtype=1
# Accept-Encoding: gzip,deflate,sdch
# Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4
# Cookie: jxtd_IP-COM_user=admin|admin|guest|0|24|3


class SWITCH_PortCfg(object):
    sw_ip='192.168.0.254'
    url="http://%s"%sw_ip
    url_lgn=url+'/cgi/login'
    headers={'Host': '%s' %sw_ip,
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
                'Content-Type': 'application/json; charset=UTF-8',
                'Referer': '%s/login.htm' %url,
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                'Cookie':'jxtd_IP-COM_user=admin|0',
                }
    headers_afterlgn={'Host': '%s' %sw_ip,
                'Connection': 'keep-alive',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36',
                'Content-Type': 'application/json; charset=UTF-8',
                'Referer': 'http://192.168.0.254/cgi/login?username=admin&password=admin',
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                'Cookie':'jxtd_IP-COM_user=admin|0',
                }
    def __init__(self,user="admin",pwd="admin",dutip="192.168.0.254"):
        self.user=user
        self.pwd=pwd
        #self.dutip=dutip
        url=self.url_lgn+'?username=%s&password=%s'%(self.user,self.pwd)
        #http://192.168.0.254/cgi/login?username=admin&password=admin
        #data={'password':'%s' %base64.b64encode(self.pwd)}
        req=requests.get(url,headers=self.headers)
        #req=requests.post(url,data=data)
        # url1=self.url+'/'
        # eq=requests.get(url1,headers=self.headers_afterlgn)
        #print req.text
    port_cfg={
    '1':'OFF',
    '2':'OFF',
    '3':'OFF',
    '4':'OFF',
    '23':'100',
    }
    def get_portlist_check(self,opt='STATE',**args):
        #opt STATE SPEED
        #/cgi/get_port?rand=0.9413318247534335
        url=self.url+"/cgi/get_port?rand=0.9413318247534335"
        req=requests.get(url,headers=self.headers_afterlgn)
        pagelists=req.text.split('|')
        #lenth=len(str)
        #print str[1:lenth-2].split(',')
        rv=False
        for key in args:
            portlist=pagelists[int(key)-1]
            lenth=len(portlist)
            linkstatus=portlist[1:lenth-2].split(',')[1].split(':')[1]
            state=portlist[1:lenth-2].split(',')[2].split(':')[1]
            if opt == 'UPTST' and int(linkstatus) !=0:
                rv=True            
            if opt == 'STATE' and state==args[key]:
                rv=True
                # if args[key]=='0' and linkstatus != '0':
                    # rv=False
                # elif args[key]!='0' and linkstatus =='0':
                    # rv=False
                #if int(args[key])*int(linkstatus) ==0:
                    #return False
            if opt== 'SPEED' and linkstatus==args[key]:
                rv=True
        return rv
    def check_cfg(self,timeout=30,**args):
        rv=True
        port_args={}
        #state ON OFF
        intf_mode={'AUTO':'0','10H':'1','10F':'2','100H':'3','100':'4','1000':'5'}
        for key in args:
            if args[key] in ['ON','OFF']:
                opt="STATE"
            else:
                opt="SPEED"

            if args[key] == 'ON':
                port_args[key]='1'
            elif args[key] == 'OFF':
                port_args[key]='0'
            else:
                port_args[key]=intf_mode[args[key]]

        i=0
        print port_args
        while self.get_portlist_check(opt,**port_args) is not True:
            time.sleep(1)
            print i
            i+=1
            if i >=30:
                rv=False
                break
        return rv
    def Port_Cfg(self,cmp=0,**args):
        #'LAN':'ON'
        #'WAN':'ON'
        self.port_cfg={}
        keylist=args.keys()
        if 'PORT_SER' in keylist:
            self.port_cfg['5']=args['PORT_SER']
        if 'PORT_IXIA' in keylist:    
            self.port_cfg['23']=args['PORT_IXIA']
        if cmp==0:
            if 'PORT_LAN' in keylist:
                self.port_cfg['2']=args['PORT_LAN']
            if 'PORT_WAN' in keylist:
                self.port_cfg['1']=args['PORT_WAN']
        else:
            if 'PORT_LAN' in keylist:
                self.port_cfg['4']=args['PORT_LAN']
            if 'PORT_WAN' in keylist:
                self.port_cfg['3']=args['PORT_WAN']
        #print self.port_cfg
        for item in self.port_cfg:
            self.Set_Port(item,self.port_cfg[item])
            
        if self.check_cfg(self.port_cfg):
            return True
        return False
    def Set_Muti_Port(self,**args):
        self.port_cfg.update(args)
        for item in self.port_cfg:
            self.Set_Port(item,self.port_cfg[item])
        if self.check_cfg(self.port_cfg):
            return True
        return False
    
    def Set_Port(self,port=0,state='ON'):
        #port 1~24
        #state ON OFF
        intf_mode={'AUTO':'0','10H':'1','10F':'2','100H':'3','100':'4','1000':'5'}
        port=port
        statecode=0
        if state == 'ON':
            statecode=1
        elif state == 'OFF':
            statecode=0
        else:
            statecode=intf_mode[state]
        if state in ['ON','OFF']:
            url=self.url+"/cgi/set_port?rand=0.5683900034055114&opt=1&port=%s&autocfg=0&state=%s&priority=0&flowcfg=0&broadcast=3&isolation=0&jumbocfg=1518"%(port,statecode)
        else:
            url=self.url+"/cgi/set_port?rand=0.1941599757410586&opt=1&port=%s&autocfg=%s&state=1&priority=0&flowcfg=0&broadcast=3&isolation=0&jumbocfg=1518"%(port,statecode)
        req=requests.get(url,headers=self.headers_afterlgn)
        
        
class Wifi_parameterConvert(object):
    def __init__(self):
        self.wifi_cfg={}
    
    def ECOS(self,**parameter):
        for item in parameter:
            if item == "SSID":
                self.wifi_cfg['wifiSSID']=parameter[item]
            elif item == "BAND":
                mode={'AUTO':'Auto','20':'20','40':'40'}
                self.wifi_cfg['wifiBandwidth']=mode[parameter[item]]
            elif item == "MODE":
                mode={'B':'b','G':'g','BG':'bg','BGN':'bgn','N':'bgn'}
                self.wifi_cfg['wifiMode']=mode[parameter[item]]
            elif item == "CH":
                self.wifi_cfg['wifiChannel']=parameter[item]
            elif item == "SEC":
                mode={'NONE':'none','WPA':'wpa-psk','WPA2':'wpa2-psk','MIX':'wpa&wpa2'}
                self.wifi_cfg['wifiSecurityMode']=mode[parameter[item]]
            elif item == "PWD":
                self.wifi_cfg['wifiPwd']=parameter[item]
            elif item == "SW":
                mode={'ON':'true','OFF':'false'}
                self.wifi_cfg['wifiEn']=mode[parameter[item]]
        return self.wifi_cfg
    def TP841(self,**parameter):
        #cfg=eval("{'SW':'ON','SSID':'Tenda_48B2E0','MODE':'B','CH':1,'SEC':'WPA2','PWD':12345678,'BAND':'0'}")
        for item in parameter:
            if item == "SSID":
                self.wifi_cfg['ssid']=parameter[item]
            elif item == "BAND":
                mode={'AUTO':'0','20':'1','40':'2'}
                self.wifi_cfg['bandwidth']=mode[parameter[item]]
            elif item == "MODE":
                mode={'B':'0','G':'1','BG':'2','N':'3','BGN':'4'}
                self.wifi_cfg['mode']=mode[parameter[item]]
            elif item == "CH":
                self.wifi_cfg['channel']=parameter[item]
            elif item == "SEC":
                self.wifi_cfg['encryption']=1
                if parameter[item] == 'NONE':
                    self.wifi_cfg['encryption']=0
            elif item == "PWD":
                self.wifi_cfg['key']=parameter[item]
            elif item == "SW":
                mode={'ON':'1','OFF':'0'}
                self.wifi_cfg['enable']=mode[parameter[item]]
        return self.wifi_cfg
class TP841_Cfg(WEB_Cfg):
    dutip="192.168.1.1"
    url="http://%s"%dutip
    wifiurl=""
                 #stok=hTc1.%7D!(uhbqK.40c!OgL.c.4ulK%3Cqqs
                 #     hTc1%2E%7D%21%28uhbqK%2E40c%21OgL%2Ec%2E4ulK%3Cqqs
                 #stok=yae%3C47B)oaD9CAk4LpSc%3COz%5DO3SuHem%3C/ds
                 #     yae%3C47B)oaD9CAk4LpSc%3COz%5DO3SuHem%3C/ds
                 #%2C%2E%5B%7Dv9Q8rwY5c0Bopdp%299pd3W%7BXx%5DBee
                 #%2C.%5B%7Dv9Q8rwY5c0Bopdp)9pd3W%7BXx%5DBee
    rebooturl=url+"/goform/sysReboot"
    restoreurl=url+"/goform/sysRestore"
    setWizardurl=url+"/goform/setWizard"
    pwd="12345678"
    wifi_cfg={
        'bandwidth':'1',
        'channel':'5',
        'enable': '1',
        'encryption':'1',
        'isolate':'0',
        'key':'12345678',
        'mode':'4',
        'power':'0',
        'seccheck':'1',
        'ssid':'TP-LINK_AA65lmt',
        'ssidbrd':'1',
        'turboon':'1',
        }
    headers={'Host': '%s' %dutip,
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'http://%s' % dutip,
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
                'Content-Type': 'application/json; charset=UTF-8',
                'Referer': 'http://%s' % url,
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                }
    def __init__(self,user="admin",pwd="0KcgeX929TefbwK",dutip="192.168.1.1"):
        for i in range(0,1):
            # try:
            #print "***********TP841"
            
            
            self.user=user
            self.pwd=pwd
            self.dutip=dutip
            url="http://%s" %(self.dutip)
            data={'method':'do','login':{'password':'0KcgeX929TefbwK'}}
                                                     
            jdata = json.dumps(data)         # 对数据进行JSON格式化编码
            req=requests.post(url,data=jdata)
            datas=demjson.decode(req.text)
            if datas.get('error_code') != 0:
                #print "login fail~"
                return False
            #TP841登录成功后 路由器返回一个 类似sesionID的东西 可以组合成request URL进行其他的访问
            #print "datas=%s"%datas
            self.wifiurl=url+"/stok=%s/ds"%(datas.get('stok')) 
            #print "wifiurl=%s"%self.wifiurl
            
            #c%2ChAD%2Bsb%5D%7CkjC%3E%7BYwCH%5BaGC**%7CCwhCqt
            #c%2ChAD%2Bsb%5D%7CkjC%3E%7BYwCH%5BaGC**%7CCwhCqt
            #c%2ChAD%2Bsb%5D%7CkjC%3E%7BYwCH%5BaGC%2A%2A%7CCwhCqt
            #self.wifiurl="%s"%urllib.unquote(urllib.quote("hTc1%2E%7D%21%28uhbqK%2E40c%21OgL%2Ec%2E4ulK%3Cqqs"))
            
            # a="hTc1%2E%7D%21%28uhbqK%2E40c%21OgL%2Ec%2E4ulK%3Cqqs"
            # print a
            # b=urllib.unquote("hTc1.%257D%21%28uhbqK.40c%21OgL.c.4ulK%253Cqqs")
            # b=urllib.quote_plus(a)
            # c=urllib.unquote_plus(b)
            # print b
            # print c
            # print urllib.quote(urllib.unquote("hTc1%2E%7D%21%28uhbqK%2E40c%21OgL%2Ec%2E4ulK%3Cqqs"))
            # print urllib.unquote(urllib.unquote(urllib.quote(urllib.unquote("hTc1%2E%7D%21%28uhbqK%2E40c%21OgL%2Ec%2E4ulK%3Cqqs")))
            # print "hTc1.%7D!(uhbqK.40c!OgL.c.4ulK%3Cqqs"
            #matchobj=re.match(r'(\W):(\W)',datas,re.M|re.X)
            #num = re.sub(r'#.*$', "", data)
            #print data[u'datetime_1']
            #print matchobj.group()
            #print req.url
            # print dir(req)
            #self.cookies=req.cookies
            #if req.url.find('quickset') != -1:
                #req=requests.post(self.setWizardurl,data="wanType=dhcp",headers=self.headers)
    def set_wifi(self,**args):
        #self.login(user,pwd,ip)
        #转化WIFI参数
        #conFunc=self.__class__.__name__.split("_")[0]
        #print conFunc
        #conObj=Wifi_parameterConvert()
        args=getattr(Wifi_parameterConvert(),self.__class__.__name__.split("_")[0])(**args)
        
        #print "wifiargs=%s"%args
        
        #return
        self.wifi_cfg.update(args)
        if self.wifi_cfg['encryption']==0:
            self.wifi_cfg['key']=""
        
        data={'method':'set','wireless':{'wlan_host_2g':self.wifi_cfg}}
        jdata = json.dumps(data)
        req=requests.post(self.wifiurl,data=jdata,headers=self.headers)
        datas=demjson.decode(req.text)
        if datas.get('error_code') != 0:
                return False
        return True
        #print req.status_code
        #print req.url
        # if req.url == self.wifiurl:
            # print "web config suc!"
            # return True
        # else:
            # print "web config fail!"
            # return False
class ECOS_Cfg(WEB_Cfg):
    dutip="192.168.0.1"
    url="http://%s"%dutip
    wifiurl=url+"/goform/setWifi"
    rebooturl=url+"/goform/sysReboot"
    restoreurl=url+"/goform/sysRestore"
    setWizardurl=url+"/goform/setWizard"
    pwd="admin"
    wifi_cfg={
        'GO':'%s'%wifiurl,
        'wifiEn':'true',
        'wifiSSID':'LMT111',
        'wifiSecurityMode':'none',
        'wifiPwd':'123123123',
        'wifiHideSSID':'false',
        'wifiPower':'normal',
        'wifiTimeEn':'false',
        'wifiTimeClose':'00:00-07:00',
        'wifiTimeDate':'01111100',
        'wifiMode':'bgn',
        'wifiChannel':'6',
        'wifiBandwidth':'40'
    }
    headers={'Host': '%s' %dutip,
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Origin': 'http://%s' % dutip,
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': 'http://%s' % url,
                'Accept-Encoding': 'gzip,deflate,sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                'Cookie': "bLanguage=en; ecos_pw=%smfw:language=cn" % base64.b64encode(pwd)
                }
    def __init__(self,user="admin",pwd="admin",dutip="192.168.0.1"):
        for i in range(0,1):
            # try:
            #print "***********",user,pwd,dutip
            #print "***********ECOS"
            self.user=user
            self.pwd=pwd
            self.dutip=dutip
            url="http://%s/login/Auth" %(self.dutip)
            data={'password':'%s' %base64.b64encode(self.pwd)}
            requests.get("http://%s" %(self.dutip))
            req=requests.post(url,data=data)
           # print dir(req)
            self.cookies=req.cookies
            if req.url.find('quickset') != -1:
                req=requests.post(self.setWizardurl,data="wanType=dhcp",headers=self.headers)
            #print req.cookies.get_dict()
           # print req.status_code
           # print req.url
    # def update_baseinfo(self,user="admin",pwd="admin",dutip="192.168.0.1"){
    
    # }
    def update_dict(self,item_dict,args):
        #更新字典数据函数
        item_dict=item_dict
        input_keys=set(args.keys())
        default_keys=set(item_dict.keys())
        diff=input_keys-default_keys
        if diff:
            print u"参数错误:" ",".join(list(diff))
            return
        new_config=deepcopy(item_dict)
        new_config.update(args)
        return new_config
    def set_wifi(self,**args):
        #self.login(user,pwd,ip)
        args=getattr(Wifi_parameterConvert(),self.__class__.__name__.split("_")[0])(**args)
        self.wifi_cfg.update(args)
        # headers={'Host': '%s' %(self.ip),
                # 'Connection': 'keep-alive',
                # 'Accept': '*/*',
                # 'Origin': 'http://%s' % (self.ip),
                # 'X-Requested-With': 'XMLHttpRequest',
                # 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
                # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'Referer': 'http://%s' % self.wifiurl,
                # 'Accept-Encoding': 'gzip,deflate,sdch',
                # 'Accept-Language': 'zh-CN,zh;q=0.8',
                # 'Cookie': "bLanguage=en; ecos_pw=%smfw:language=cn" % base64.b64encode(self.pwd)
                # }
        #print "self.wifi_cfg=%s"%self.wifi_cfg
        req=requests.post(self.wifiurl,data=self.wifi_cfg,headers=self.headers)
        #print req.status_code
        #print req.url
        if req.url == self.wifiurl:
            #print "web config suc!"
            return True
        else:
            #print "web config fail!"
            return False
    def reboot(self):
        req=requests.post(self.rebooturl,data="action=reboot",headers=self.headers)
        
    def restore(self):
        req=requests.post(self.restoreurl,data="action=restore",headers=self.headers)
if __name__=="__main__":
   #web_cfg=TP841_Cfg()
   #web_cfg=ECOS_Cfg()
   web_cfg=SWITCH_PortCfg()
   #str="{'PORT_LAN':'PORT_ON','PORT_WAN':'ON','PORT_SER':'ON'}"
   #cfg=eval(str)
   print web_cfg.check_cfg(**eval("{'1':'OFF'}"))
   
   
   
   #str="{'wifiSSID':'Tenda_48B2E0','wifiMode':'b','wifiChannel':'1','wifiSecurityMode':'wpa2-psk','wifiPwd':'12345678'}"
   #cfg=eval("{'SW':'ON','SSID':'Tenda_48B2E0125','MODE':'B','CH':13,'SEC':'MIX','PWD':123456782,'BAND':'AUTO'}")
   
   #cfg=eval("{'SW':'ON','SSID':'Tenda_48B2E0','MODE':'BGN','CH':5,'SEC':'NONE','PWD':'12346578','BAND':'20'}")
   #cfg=eval("{'SW':'OFF'}")
   #cfg=eval(str)
   #print cfg
   #time.sleep(5)
   #print web_cfg.set_wifi(user="admin",pwd="12345678",ip="192.168.1.1",**cfg)