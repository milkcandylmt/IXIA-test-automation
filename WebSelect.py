#encoding=utf-8
import WebConfig
from WebConfig import *
class Http_Cfg(WEB_Cfg):
    def __init__(self):
        self.switch_args={}
        self.testdut_args={}
    def do_args(self,product="ECOS",user="admin",pwd="admin",dutip="192.168.0.1",cmp=0,**args):
        rv=False
        self.testdut_args.update(args)
        
        for key in args:
            if key.startswith('PORT_'):
                self.switch_args[key]=self.testdut_args.pop(key)
        
        
        cls=getattr(WebConfig,"%s_Cfg"%product)
        if cls and len(self.testdut_args)!=0:
            if cls(user,pwd,dutip).set_wifi(**args):
                rv=True
                
        #交换机配置放在最后 防止配置完交换机无法配置产品        
        # if len(self.switch_args)!=0:
            # if SWITCH_PortCfg().Port_Cfg(cmp,**self.switch_args):
                # rv=True
        return rv
            #print ins
# clss=WebConfig.WEB_Cfg.__subclasses__()
# print [x for x in clss if x.__name__ =="ECOS_Cfg"][0]
if __name__=="__main__":
   #web_cfg=TP841_Cfg()
   #web_cfg=ECOS_Cfg()
   #str="{'PORT_IXIA':'100','PORT_WAN':'ON','PORT_SER':'ON','SW':'ON','SSID':'Tenda_48B2E0125'}"
   str="{'PORT_IXIA':'100'}"
   cfg=eval("{'PORT_IXIA':'100'}")
   web_cfg=Http_Cfg().do_args(**eval("{'PORT_IXIA':'100'}"))
   
   #web_cfg.Port_Cfg(1,)
   
