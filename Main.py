#coding=utf-8
from UI import Ui_MainWindow
from WebConfig import ECOS_Cfg
import WebConfig
from WebSelect import Http_Cfg
from WebConfig import *
import Report
import sys,os,Tkinter
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from configobj import ConfigObj
from DIY_CaseTreeWidget import *
import subprocess
import threading
import Queue,time
import sys
import shutil
import datetime
#from Global import *
#跨文件全局变量修改生效

import Global as GlobalVar
from global_net import *


import qt4reactor
qt4reactor.install()
# from twisted.application import reactors
# reactors.installReactor('qt4')
import re
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor

import serial
import paramiko
#IP地址操作模块
from IPy import IP


reload(sys)
sys.setdefaultencoding('utf-8')
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)





tcl_obj=Tkinter.Tcl()
#tcl_obj.evalfile("main.tcl");

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
workq = Queue.Queue(0)
def cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
mainpath=cur_file_dir();
#生成腾达报告的路径，全局变量
#reportpath=""
reportpath=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
reportpath=os.path.join("tendareport",reportpath)
reportpath=os.path.join(mainpath,reportpath)
if not os.path.exists(reportpath):
    os.makedirs(reportpath)
Debug_logfile=os.path.join(reportpath,"run_log.log")
Debug_logfile=os.path.join(mainpath,Debug_logfile)



# port_init={
    # '1':'OFF',   #DUT WAN   
    # '2':'OFF',    #DUT LAN
    # '3':'OFF',   #CMP WAN
    # '4':'OFF',    #CMP LAN
    # '5':'OFF',   #SER
    # '23':'100', #交换机的IXIA直连接口 设置接口速率 100 1000 全双工
    # }
# port_init1={
    # '1':'OFF',   #DUT WAN   
    # '2':'OFF',    #DUT LAN
    # '3':'OFF',   #CMP WAN
    # '4':'OFF',    #CMP LAN
    # }
# def Port_Init(**args):
    # if SWITCH_PortCfg().Set_Muti_Port(**args):
                # return 1
    # else:
        # return 0
    
    
testscript="unicast_unidirectional_throughput"
dir_auto=""
dir_python=""
config_path=""
#cmp_flag用于标志是否加入竞品
cmp_flag=0

#run_flag用于标识run_test()函数是否已经执行过
run_flag=0
#起一个线程的原因是，在线程中等待进程完成
#结束时，先清空工作队列，然后将当前的工作进程杀死，线程自动退出

#开启服务器
# factorydir=os.path.join(mainpath,"factory\\factory_2.py")
# appname="python %s" % factorydir
#self.factoryprocess=subprocess.Popen(appname,creationflags=subprocess.CREATE_NEW_CONSOLE)
# factoryprocess=subprocess.Popen(appname)


def check_net(server,timeout=0.5):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        ret=sock.connect(server)
        sock.send("quit\r\n")
        print sock.recv(1024)
        sock.close()
        return 1
    except:
        return 0
class Echo(Protocol):
  def __init__(self,factory):
    self.factory=factory
  def dataReceived(self, data):
    if data.startswith('welcome'):
        self.transport.getHandle().sendall("regist\r\n")
        self.factory.Connected()
        print "regist"

class EchoClientFactory(ReconnectingClientFactory):
    def __init__(self,window):
        self.win=window
    def startedConnecting(self, connector):
        print 'Started to connect to factory.'
    # def setLunchResult(self,data):
        # self.win.setLunchResult(data)
    # def setProcessAlive(self,data):
        # self.win.setProcessAlive(data)
    # def setPing(self,data):
        # self.win.setPing(data)
    def Connected(self):
        self.win.Connected()
    def buildProtocol(self, addr):
        print 'Connected.'
        print 'Resetting reconnection delay'
        self.resetDelay()
        return Echo(self)
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,reason)     

class TreeWidgetItem(CaseWidgetItem):
    def __init__(self,id,parent=None):
        CaseWidgetItem.__init__(self,parent)
        self.id=id
#起一个线程的原因是，在线程中等待进程完成
class RunThread(QThread):
    global config_path,cmp_flag
    sinOut = pyqtSignal(str)
    def __init__(self,product="",user="",pwd="",dutip="",product_cmp="",user_cmp="",pwd_cmp="",url_cmp="",parent=None):
        super(RunThread,self).__init__(parent)
        self.p=None
        #self.web_config=ECOS_Cfg(user,pwd,dutip)
        self.product=product
        self.user=user
        self.pwd=pwd
        self.dutip=dutip
        self.product_cmp=product_cmp
        self.user_cmp=user_cmp
        self.pwd_cmp=pwd_cmp
        self.dutip_cmp=url_cmp
        web_config_dut=product
        web_config_cmp=product_cmp
        self.webcfg_obj=Http_Cfg()
        # cls_dut=getattr(WebConfig,"%s_Cfg"%product)
        # self.web_config_dut=cls_dut(user,pwd,dutip)
        # if cmp_flag == 1:
            ### self.sinOut.emit(u"aaaaaaaaaaa:%s"%unicode(str(product_cmp),"utf-8"))
            # cls_cmp=getattr(WebConfig,"%s_Cfg"%product_cmp)
            # if  cls_cmp is not None:
                # self.web_config_cmp=cls_cmp(user_cmp,pwd_cmp,url_cmp)
    def run(self):
        while True:
            try:
                configweb,case_name,exec_str,steps,testdut=workq.get_nowait()
                wmlpath=os.path.join(mainpath,"cases\%s\%s.tcl"%(steps,case_name))
                self.sinOut.emit(unicode(str(testdut+":"+wmlpath),"utf-8"))
                #self.sinOut.emit(unicode(str(exec_str),"utf-8"))
                # if os.path.exists(config_path):
                    # os.remove(config_path)
                if not os.path.exists(unicode(str(wmlpath),"utf-8")):
                    self.sinOut.emit(u"tcl用例不存在:%s"%unicode(str(wmlpath),"utf-8"))
                    continue

                #给主线程发射消息
                #Port_Init(**port_init1)
                
                #port_set={'PORT_LAN':'ON'}
                #self.rs = self.webcfg_obj.do_args(product=testdut,user=user,pwd=pwd,dutip=dutip,cmp=cmp,**configweb_args)
                
                #WEB配置参数处理
                configweb_args=eval(configweb)
                cmp=0
                user=None
                pwd=None
                dutip=None
                if testdut == self.product:
                    cmp=0
                    user=self.user
                    pwd= self.pwd
                    dutip=self.dutip
                else:
                    cmp=1
                    user=self.user_cmp
                    pwd=self.pwd_cmp
                    dutip=self.dutip_cmp
                #开启交换机直连的 testdut配置LAN口
                # if self.webcfg_obj.do_args(product=testdut,user=user,pwd=pwd,dutip=dutip,cmp=cmp,**port_set):
                    # self.sinOut.emit(u"LAN口启动成功")
                
                self.rs = self.webcfg_obj.do_args(product=testdut,user=user,pwd=pwd,dutip=dutip,cmp=cmp,**configweb_args)
               
                self.sinOut.emit(unicode(str(self.rs),"utf-8"))
                
                
                #time.sleep(3)
                self.p=subprocess.Popen(exec_str,creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.p.wait()
                
                #关闭DUT无线
                self.rs = self.webcfg_obj.do_args(product=testdut,user=user,pwd=pwd,dutip=dutip,cmp=cmp,**eval("{'SW':'OFF'}"))
                self.sinOut.emit(unicode(str(self.rs),"utf-8"))
                

            except Exception,e:
                if not workq.empty():
                    continue
                if e:
                    if str(e):
                        self.sinOut.emit(unicode(str(e),"utf-8"))
                        return
                    else:
                        self.sinOut.emit(u"运行结束")
                        return




#结束时，先清空工作队列，然后将当前的工作进程杀死，线程自动退出
class RunThread_1(QThread):
    global config_path,cmp_flag
    sinOut = pyqtSignal(str)
    def __init__(self,product="",user="",pwd="",dutip="",product_cmp="",user_cmp="",pwd_cmp="",url_cmp="",parent=None):
        super(RunThread,self).__init__(parent)
        self.p=None
        #self.web_config=ECOS_Cfg(user,pwd,dutip)
        self.product=product
        self.user=user
        self.pwd=pwd
        self.dutip=dutip
        self.product_cmp=product_cmp
        self.user_cmp=user_cmp
        self.pwd_cmp=pwd_cmp
        self.dutip_cmp=url_cmp
        web_config_dut=product
        web_config_cmp=product_cmp
        cls_dut=getattr(WebConfig,"%s_Cfg"%product)
        self.web_config_dut=cls_dut(user,pwd,dutip)
        if cmp_flag == 1:
            #self.sinOut.emit(u"aaaaaaaaaaa:%s"%unicode(str(product_cmp),"utf-8"))
            cls_cmp=getattr(WebConfig,"%s_Cfg"%product_cmp)
            if  cls_cmp is not None:
                self.web_config_cmp=cls_cmp(user_cmp,pwd_cmp,url_cmp)
    def run(self):
        while True:
            try:
                configweb,case_name,exec_str,steps,testdut=workq.get_nowait()
                wmlpath=os.path.join(mainpath,"cases\%s\%s.tcl"%(steps,case_name))
                self.sinOut.emit(unicode(str(testdut+":"+wmlpath),"utf-8"))
                #self.sinOut.emit(unicode(str(exec_str),"utf-8"))
                # if os.path.exists(config_path):
                    # os.remove(config_path)
                if not os.path.exists(unicode(str(wmlpath),"utf-8")):
                    self.sinOut.emit(u"tcl用例不存在:%s"%unicode(str(wmlpath),"utf-8"))
                    continue

                #给主线程发射消息
    
                configweb_args=eval(configweb)
                ######web_cfg=ECOS_Cfg().set_wifi(**configweb)
                #self.web_config.set_wifi(**configweb)
                #配置DUT无线参数
                if testdut == self.product:
                    self.sinOut.emit(unicode(str("====dut"),"utf-8"))
                    self.rs=self.web_config_dut.set_wifi(**configweb_args)
                elif testdut == self.product_cmp:
                    self.sinOut.emit(unicode(str("====cmp"),"utf-8"))
                    self.rs=self.web_config_cmp.set_wifi(**configweb_args)
                else:
                    self.sinOut.emit(u"产品WIFI配置错误:%s"%unicode(str(testdut),"utf-8"))
                    continue
                self.sinOut.emit(unicode(str(self.rs),"utf-8"))
                
                
                #time.sleep(3)
                self.p=subprocess.Popen(exec_str,creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.p.wait()
                
                #关闭DUT无线
                if testdut == self.product:
                    self.rs=self.web_config_dut.set_wifi(**eval("{'SW':'OFF'}"))
                elif testdut == self.product_cmp:
                    self.rs=self.web_config_cmp.set_wifi(**eval("{'SW':'OFF'}"))
                else:
                    self.sinOut.emit(u"产品WIFI配置错误:%s"%unicode(str(testdut),"utf-8"))
                    continue
                self.sinOut.emit(unicode(str(self.rs),"utf-8"))
                

            except Exception,e:
                if not workq.empty():
                    continue
                if e:
                    if str(e):
                        self.sinOut.emit(unicode(str(e),"utf-8"))
                        return
                    else:
                        self.sinOut.emit(u"运行结束")
                        return
class Serial_DIY(object):        
    def __init__(self,COM,baudrate):
        self.atten_init(COM,baudrate)
    def atten_init(self,COM,baudrate):
        self.atten_serialObj=serial.Serial(
        #port=unicode(self.ui.atten_COM.currentText()),              # number of device, numbering starts at  
        port=COM,
        # zero. if everything fails, the user  
        # can specify a device string, note  
        # that this isn't portable anymore  
        # if no port is specified an unconfigured  
        # an closed serial port object is created  
        baudrate=baudrate,          # baud rate  
        bytesize=serial.EIGHTBITS,     # number of databits  
        parity=serial.PARITY_NONE,     # enable parity checking   奇偶校验
        stopbits=serial.STOPBITS_ONE,  # number of stopbits  
        timeout=0.1,           # set a timeout value, None for waiting forever  
        xonxoff=0              # enable software flow control  
        #rtscts=0,               # enable RTS/CTS flow control  
        #interCharTimeout=None   # Inter-character timeout, None to disable 
        )
    def atten_opt(self,cmd):
        if cmd is not None and cmd !="":
            #self.atten_serialObj.open()
            #print self.atten_serialObj.readline()
            self.atten_serialObj.write(cmd)
            self.atten_serialObj.write("\n")
            print "write suc"
            #print self.atten_serialObj.readline()
            #self.atten_serialObj.close()
            # i=0
            while 1:
                 print self.atten_serialObj.readline()
                 if self.atten_serialObj.readline() == "":
                    break
               
#重定向到testlog框
class Redirect(object):
    def __init__(self,editor):
        self.editor=editor
        self.stdout=sys.stdout
    def write(self,writestr):
    
        #isinstance（）判断writestr对象类型是否为QString，是则返回True
        if isinstance(writestr,QString):
            writestr=unicode(writestr)
        writestr=writestr.strip()
        if writestr:
            if not isinstance(writestr,unicode):
                try:
                    writestr=writestr.decode("gbk")
                except:
                    writestr=writestr.decode("utf-8")
        self.editor.append(writestr)

    
        
        
        
class MainWindow(QMainWindow):
    def __init__(self,parent=None):
       # os.chdir(mainpath);
        super(MainWindow,self).__init__(parent)
        # self.status = self.statusBar()
        # self.status.showMessage("This is StatusBar",5000)
        # self.setWindowTitle("PyQt MianWindow")
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        #print "self=",self
        #print "self.dir=",dir(self)
        #cls=getattr(WebConfig,"%s_Cfg"%product)
        
        #根据WebConfig模块里面的类名*_Cfg 更新下拉表单的数据
        pi=0
        for item in dir(WebConfig):
            rm=re.search("_Cfg",item)
            if rm is not None and item != "WEB_Cfg":
                self.ui.dut_type.setItemText(pi, _translate("MainWindow", item.split("_")[0], None))
                self.ui.cmp_type.setItemText(pi, _translate("MainWindow", item.split("_")[0], None))
                pi=pi+1
        
        
        #将sys.stdout的write函数重写为Redirect的write函数,Redirect重定向到testlog框
        #需重点理解
        
        self.stdout=Redirect(self.ui.testlog)
        sys.stdout=self.stdout
        
        #初始化树
        self.init_tree()
        
        #加载配置文件
        self.configfile=os.path.join(mainpath,"config.ini")
        self.selectfile=os.path.join(mainpath,"selected.ini")
        self.load_config()
        
        #设置UI界面连接
        self.ui.btn_save.clicked.connect(self.save_config)
        self.ui.btn_auto.clicked.connect(self.get_auto)
        self.ui.btn_tcl.clicked.connect(self.get_tcl)
        self.ui.btn_python.clicked.connect(self.get_python)
        self.ui.btn_run.clicked.connect(self.run_test)
        self.ui.btn_log.clicked.connect(self.set_log)
        self.ui.btn_stop.clicked.connect(self.run_stop)
        self.ui.rep_btn.clicked.connect(self.make_test_report)
        
        self.init_login()
        #print "product_cmp=%s"%self.product_cmp
        #print "login=",self.product,self.user,self.pwd,self.url
        self.init_tcl()
        self.p=None
        self.time_start=None
        self.time_end=None
        self.reportdirname=""
        
        #初始化交换机接口
        #print Port_Init(**port_init)
        
        #self.atten_init()
        #self.atten_opt("A,20")
        #串口操作
        # self.workthread=None
        # if run_flag==1 and workq.empty() and  self.make_report:
        #启动factory
        #self.factorydir=os.path.join(mainpath,"factory\\factory_2.py")
        #appname="python %s" % self.factorydir
        #self.factoryprocess=subprocess.Popen(appname,creationflags=subprocess.CREATE_NEW_CONSOLE)
        #self.connection=None
        #self.factoryprocess=factoryprocess
        #time.sleep(1)
        #self.Connect2Factory()
    def atten_init(self):
        self.atten_serialObj=serial.Serial(
        #port=unicode(self.ui.atten_COM.currentText()),              # number of device, numbering starts at  
        port="COM8",
        # zero. if everything fails, the user  
        # can specify a device string, note  
        # that this isn't portable anymore  
        # if no port is specified an unconfigured  
        # an closed serial port object is created  
        baudrate=9600,          # baud rate  
        bytesize=serial.EIGHTBITS,     # number of databits  
        parity=serial.PARITY_NONE,     # enable parity checking  
        stopbits=serial.STOPBITS_ONE,  # number of stopbits  
        timeout=None,           # set a timeout value, None for waiting forever  
        xonxoff=0,              # enable software flow control  
        rtscts=0,               # enable RTS/CTS flow control  
        interCharTimeout=None   # Inter-character timeout, None to disable 
        )
    def atten_opt(self,cmd):
        if cmd is not None and cmd !="":
            #self.atten_serialObj.open()
            self.atten_serialObj.write(cmd)
            print "write suc"
            i=0
            while 1:
                print self.atten_serialObj.readline()
                time.sleep(0.1)
                i+=1
                if i>=30:
                    break
            #
    def closeEvent(self, event):
        #关闭窗口时,停止服务
        # running_process=[runname for runname in self.lunchstate.keys() if self.lunchstate[runname]]
        # if running_process:
            # button=QtGui.QMessageBox.question(self,u"请回答",  
                                # u"还有测试没有停止，是否自动停止?",  
                                # QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,  
                                # QtGui.QMessageBox.Ok)  
            # if button==QtGui.QMessageBox.Ok:  
                # for process in running_process:
                    # self.connection.transport.getHandle().sendall("command lunch %s %s\r\n" % (process,'stop'))
                    # self.lunchstate[process]=False
                    # print u"服务:%s 停止" % process
                # time.sleep(0.5)
        if self.connection:
            self.connection.transport.getHandle().sendall("quit\r\n")
            time.sleep(0.1)
                        # self.connection.transport.getHandle().sendall("")
            self.connection.disconnect()
        if self.factoryprocess:
            self.factoryprocess.terminate()
            self.factoryprocess=None;
        event.accept()
    def Connect2Factory(self):
        if not check_net(('127.0.0.1',10087)):
            QtGui.QMessageBox.critical(self,u"错误提示",u"factory服务器连接不上，请检查连接!")  
            return
        if not self.connection:
            self.connection=reactor.connectTCP('127.0.0.1',10087,EchoClientFactory(self))    
    def Connected(self):
        QtGui.QMessageBox.information(self,u"成功提示",u"连接成功") 
    def make_test_report(self):
        os.chdir(mainpath)
        global reportpath,testscript,tcl_obj
        self.init_devargs()
        
        select_case_ids={}
        cls=getattr(Report,"Rep_Action1")
        reportobj=cls()
        cls2=getattr(Report,"Do_Excel_V2")
        reportExcel=cls2(reportpath=reportpath)
        # if reportpath=="":
            # reportpath=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            # reportpath=os.path.join("tendareport",reportpath)
        # self.reportdirname=reportpath
        #print self.reportdirname
        if 1:
            #得到所有勾选的内容
            #print "self.root.childCount()=",self.root.childCount()
            for i in range(self.root.childCount()):
                item=self.root.child(i)
                #print "item.text=",item.text(0)
                if item.checkState(0)!=Qt.Unchecked:
                    item_name=str(item.text(0))
                    select_case_ids[item_name]=[]
                #print "item.childCount()=",item.childCount()
                for j in range(item.childCount()):
                    case_item=item.child(j)
                    if case_item.checkState(0)==Qt.Checked:
                        select_case_ids[item_name].append(case_item.id)
                    # print "case_checked=",case_item.id
            # if not select_case_ids:
                # QMessageBox.information(self,"Information",u"请选择用例") 
                # return
            # print "select_case_ids[item_name]=",select_case_ids[item_name]
            for each_item,case_ids in select_case_ids.iteritems():
                #print "each_item=%s"%each_item
                tclfile=tcl_obj.eval( "source cases/%s.tcl" % each_item )
                #print "tclfile=%s"%tclfile
                for case_id in case_ids:
                    #time.sleep(1)
                    #print "case_id=%s"%case_id
                    # print "~~"%eval(tcl_obj.eval("getargs %s" % case_id))
                    #print "caselmt=%s"%eval(tcl_obj.eval("getargs %s" % case_id))
                    (case_name,repos)=eval(tcl_obj.eval("getpos %s" % case_id))
                    #print len(case_name)
                    rspath=os.path.join(self.product,case_name)
                    # if reportobj.make_report(casename=rspath,runscript=testscript,dstpath=reportpath,dstpos=repos,rssi_check=(1,-35,-25)):
                        # print "make report error!"
                    # else:
                        # print "%s report maked suc!!report:%s"%(rspath,reportpath)
                    # if cmp_flag==1:
                        # rspath=os.path.join(self.product_cmp,case_name)
                        # if reportobj.make_report(casename=rspath,runscript=testscript,dstpath=reportpath,dstpos=repos,make_cmp=cmp_flag,rssi_check=(1,-35,-25)):
                            # print "make report error!"
                        # else:
                            # print "%s report maked suc!!report:%s"%(rspath,reportpath)
                    #print reportobj.get_csv_throughput(casename=rspath,dstpos=repos)
                    #rspath=os.path.join(self.product_cmp,case_name)
                    #print reportobj.get_csv_throughput(casename=rspath,dstpos=repos)
                    if reportExcel.writeExcel(dstpos=repos,data=reportobj.get_csv_throughput(casename=rspath,dstpos=repos)) is not True:
                       print "make report error!"
                    else:
                        print "%s report maked suc!!report:%s"%(rspath,reportpath)
                    if cmp_flag==1:
                        rspath=os.path.join(self.product_cmp,case_name)
                        if reportExcel.writeExcel(dstpos=repos,data=reportobj.get_csv_throughput(casename=rspath,dstpos=repos),make_cmp=cmp_flag) is not True:
                            print "make report error!"
                        else:
                            print "%s report maked suc!!report:%s"%(rspath,reportpath)
        reportExcel.save_excel()      
    def make_test_report_1(self):
        os.chdir(mainpath)
        global reportpath,testscript,tcl_obj
        self.init_devargs()
        
        select_case_ids={}
        cls=getattr(Report,"Rep_Action1")
        reportobj=cls()
        # if reportpath=="":
            # reportpath=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            # reportpath=os.path.join("tendareport",reportpath)
        # self.reportdirname=reportpath
        if 1:
            #得到所有勾选的内容
            for i in range(self.root.childCount()):
                item=self.root.child(i)
                if item.checkState(0)!=Qt.Unchecked:
                    item_name=str(item.text(0))
                    select_case_ids[item_name]=[]
                for j in range(item.childCount()):
                    case_item=item.child(j)
                    if case_item.checkState(0)==Qt.Checked:
                        select_case_ids[item_name].append(case_item.id)
            # if not select_case_ids:
                # QMessageBox.information(self,"Information",u"请选择用例") 
                # return
            for each_item,case_ids in select_case_ids.iteritems():
                tclfile=tcl_obj.eval( "source cases/%s.tcl" % each_item )
                for case_id in case_ids:
                    time.sleep(1)
                    (case_name,repos)=eval(tcl_obj.eval("getpos %s" % case_id))
                    rspath=os.path.join(self.product,case_name)
                    if reportobj.make_report(casename=rspath,runscript=testscript,dstpath=reportpath,dstpos=repos,rssi_check=(1,-35,-25)):
                        print "make report error!"
                    else:
                        print "%s report maked suc!!report:%s"%(rspath,reportpath)
                    if cmp_flag==1:
                        rspath=os.path.join(self.product_cmp,case_name)
                        if reportobj.make_report(casename=rspath,runscript=testscript,dstpath=reportpath,dstpos=repos,make_cmp=cmp_flag,rssi_check=(1,-35,-25)):
                            print "make report error!"
                        else:
                            print "%s report maked suc!!report:%s"%(rspath,reportpath)
        
    def run_stop(self):
        if not workq.empty():
            workq.queue.clear()
        if self.workthread:
           self.workthread.p.terminate()
    def init_tcl(self):
        # tcl_obj=Tkinter.Tcl()
        global tcl_obj
        tcl_obj.evalfile("main.tcl");
    def init_login(self):
        self.product=unicode(self.ui.dut_type.currentText())
        self.user=unicode(self.ui.dut_user.text())
        self.pwd=unicode(self.ui.dut_pwd.text())
        self.url=unicode(self.ui.dut_ip.text())
    def init_devargs(self):
        global cmp_flag
        self.make_cmp=0
        cmp_flag=0
        #self.product_cmp=""
        self.product=unicode(self.ui.dut_type.currentText())
        self.user=unicode(self.ui.dut_user.text())
        self.pwd=unicode(self.ui.dut_pwd.text())
        self.url=unicode(self.ui.dut_ip.text())
        if self.ui.make_cmp.isChecked():
            self.make_cmp=1
            cmp_flag=1
            self.product_cmp=unicode(self.ui.cmp_type.currentText())
            self.user_cmp=unicode(self.ui.cmp_user.text())
            self.pwd_cmp=unicode(self.ui.cmp_pwd.text())
            self.url_cmp=unicode(self.ui.cmp_ip.text())
    def ssh_link(self,ip,username,passwd):        
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(ip,22,username,passwd,timeout=5)
                if ip == self.Serip:
                    conn_ssh['serv']=ssh
                    print "conn_serv=",conn_ssh['serv']
                return True
            except paramiko.ssh_exception.NoValidConnectionsError:
                print u'网络连接不成功'
                return False
            except paramiko.ssh_exception.AuthenticationException:
                print u'用户名或密码不正确'
                return False    
    def run_test(self):
        global run_flag,testscript,config_path,dir_auto
        #执行前首先清空队列
        if not workq.empty():
            workq.queue.clear()
        self.init_devargs()
        self.time_start=datetime.datetime.now()
        os.chdir(mainpath);
        select_case_ids={}
        item_name=""
        path=os.environ['Path']
        dir_auto=unicode(self.ui.path_auto.text())
        dir_tcl=os.path.dirname(unicode(self.ui.path_tcl.text())).replace("/","\\")
        bin_tcl=unicode(self.ui.path_tcl.text()).replace("/","\\")
        dir_python=os.path.dirname(unicode(self.ui.path_python.text())).replace("/","\\")
        config_path=os.path.join(dir_auto,"automation/conf/insert_config.tcl")
        tcl_exec_bin=os.path.join(dir_auto,"automation/bin/vw_auto.tcl")
        #dut_ssid=str(self.ui.ssid_name.text())
        parent_log_dir=unicode(self.ui.path_log.text()).replace("/","\\")
        parent_log_dir_dut=os.path.join(parent_log_dir,self.product)
        if self.make_cmp: 
            parent_log_dir_cmp=os.path.join(parent_log_dir,self.product_cmp)
        
        exec_str="%s %s" % (bin_tcl,tcl_exec_bin)
        exec_args=""
        bclean_log=self.ui.btnclean.isChecked()
        if bclean_log:
            if os.path.exists(parent_log_dir) and os.listdir(parent_log_dir):
                reply = QMessageBox.information(self,
                                    u"请确认",  
                                    u"是否删除当前目录下其他日志?",  
                                    QMessageBox.Yes | QMessageBox.No)
                if reply:
                    os.system('rd /s /q "%s"' %parent_log_dir.encode("gbk"))
                    os.makedirs(parent_log_dir.encode("gbk"))
                    os.makedirs(parent_log_dir_dut.encode("gbk"))
                    if self.make_cmp:
                        os.makedirs(parent_log_dir_cmp.encode("gbk"))
        # if not (path.find(dir_tcl)!=-1 or path.find(dir_tcl.replace("/","\\"))!=-1):
            # QMessageBox.information(self,"Information",u"添加TCL路径到环境变量") 
            # return
        # if not (dir_python in path or dir_python.lower() in path):
           # QMessageBox.information(self,"Information",u"添加Python路径到环境变量") 
           # return
        vw_auto_path=os.path.join(dir_auto,"automation/bin/vw_auto.tcl")
        if not os.path.exists(vw_auto_path):
            QMessageBox.information(self,"Information",u"自动化目录/automation/bin/vw_auto.tcl必须存在") 
            return
        #得到所有勾选的内容
        #print "self.root.childCount()=",self.root.childCount()
        for i in range(self.root.childCount()):
            item=self.root.child(i)
            if item.checkState(0)!=Qt.Unchecked:
                item_name=str(item.text(0))
                select_case_ids[item_name]=[]
            for j in range(item.childCount()):
                case_item=item.child(j)
                if case_item.checkState(0)==Qt.Checked:
                    select_case_ids[item_name].append(case_item.id)
        if not select_case_ids:
            QMessageBox.information(self,"Information",u"请选择用例") 
            return
        for each_item,case_ids in select_case_ids.iteritems():
            tclfile=tcl_obj.eval( "source cases/%s.tcl" % each_item )
            for case_id in case_ids:
                exec_str="%s %s" % (bin_tcl,tcl_exec_bin)
                #print "case_id=%s"%case_id
                (case_name,configweb,steps)=eval(tcl_obj.eval("getargs %s" % case_id))
                #steps=steps.split(",")
                #steps=[step.strip() for step in steps if step.strip()]
                #steps.extend(['keylset global_config TestList {%s}' %testscript])
                #steps="\n".join(steps)
                
                steps=each_item
                
                full_log_path=os.path.join(parent_log_dir_dut,"%s\%s"%(each_item,case_name.decode("utf-8")))
                #tcl_obj.eval( "set VW_TEST_ROOT1 %s" % each_item )
                
                
                
                # if not os.path.exists(full_log_path):
                    # os.makedirs(full_log_path)
                wmlpath=os.path.join(mainpath,"cases\%s\%s.tcl"%(steps,case_name))
                #print "wmlpath=",wmlpath
                #exec_args=' --var logdir "%s,%s" ' %(full_log_path.encode('utf-8'),wmlpath.encode('utf-8').replace("\\","/"))
                #exec_args=' --var logdir "%s" ' %full_log_path.encode('utf-8').replace("\\","/")
                
                case_log_dir=os.path.join(parent_log_dir_dut,"%s"%case_name.decode("utf-8"))
                exec_args=' --var logdir "%s" ' %case_log_dir.encode('utf-8').replace("\\","/")
                #exec_args+=' --var1 _casefile "%s" ' %full_log_path.encode('utf-8')
                exec_args+=' --var _casefile "%s" ' %wmlpath.encode('utf-8')
                #steps=full_log_path.encode('utf-8')
                # with open(config_path,"w+") as fd:
                    # fd.write(steps)
                    # fd.close()
                    
                #NAT模块网关必须为DUT的管理IP（网关） 数据才可转发出去
                conf_gw="puts 0"
                conf_ip="puts 1"
                #print each_item
                if each_item == "（5）无线NAT转发率_24G2T2R":
                    conf_gw="keylset Group_002 Gateway %s"%self.url
                    conf_ip="keylset Group_002 BaseIp %s"%IP(self.url).make_net('255.255.255.0')[111] #IP(self.url).make_net('255.255.255.0')利用IP和子网掩码生成IP网段 返回值为IP网段列表
                ipinfo_str=' --var _natipinfo "%s;%s;" '%(conf_gw,conf_ip)
                    
                exec_str_dut=exec_str+exec_args
                exec_str_dut+=ipinfo_str
                #print exec_str,repr(exec_str)
                #print "exec_str_dut=%s"%exec_str_dut
                # libdir=os.path.join(os.path.dirname(dir_tcl),"lib/vcl")
                # os.chdir(libdir)
                
                #configweb="wifiSSID='aaaaa',wifiChannel=8"
                #将脚本名称和运行脚本的命令 传入 队列workq中
                workq.put((configweb,case_name,exec_str_dut.encode('gbk'),steps,self.product))
                if self.make_cmp:
                    full_log_path_cmp=os.path.join(parent_log_dir_cmp,case_name.decode("utf-8"))
                    full_script_path=os.path.join(parent_log_dir_cmp,"%s\%s"%(each_item,case_name.decode("utf-8")))
                    if not os.path.exists(full_log_path_cmp):
                        os.makedirs(full_log_path_cmp)
                    exec_args_cmp=' --var logdir "%s" ' %full_log_path_cmp.encode('utf-8')
                    exec_args_cmp+=' --var _casefile "%s" ' %wmlpath.encode('utf-8')
                    
                    #NAT模块 网关必须为DUT的管理IP 数据才可转发出去
                    #steps.extend(['keylset global_config TestList {%s}' %testscript])
                    #steps="\n".join(steps)
                    conf_gw="puts 0"
                    conf_ip="puts 1"
                    if each_item == "（5）无线NAT转发率_24G2T2R":
                        conf_gw="keylset Group_002 Gateway %s"%self.url_cmp
                        conf_ip="keylset Group_002 BaseIp %s"%IP(self.url_cmp).make_net('255.255.255.0')[111]
                    ipinfo_str=' --var _natipinfo "%s;%s;" '%(conf_gw,conf_ip)
                    
                    
                    
                    exec_str_cmp=exec_str+exec_args_cmp
                    exec_str_cmp+=ipinfo_str
                    #print "cmp_exestr=%s"%exec_str_cmp
                    workq.put((configweb,case_name,exec_str_cmp.encode('gbk'),steps,self.product_cmp))
        libdir=os.path.join(os.path.dirname(dir_tcl),"lib/vcl")
        os.chdir(libdir)
        #print "%s,%s,%s,%s"%(self.product,self.user,self.pwd,self.url)
        
        if self.make_cmp:
            #print "%s,%s,%s,%s"%(self.product_cmp,self.user_cmp,self.pwd_cmp,self.url_cmp)
            self.workthread=RunThread(self.product,self.user,self.pwd,self.url,self.product_cmp,self.user_cmp,self.pwd_cmp,self.url_cmp)
        else:
            self.workthread=RunThread(self.product,self.user,self.pwd,self.url)
        self.workthread.sinOut.connect(self.outText)
        self.workthread.start();
    def ticklock(self):
        #>>> datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #    '2016-07-08 16:19:44'
        #(beforetime-datetime.datetime.now()).total_seconds()
        pass
    def Debug_Log(self,data):
        global Debug_logfile
        self.time_end=datetime.datetime.now()
        datas=data
        data="%s  %s"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),data)
        #print u"aaa=%s"%reportpath
        fd=open(Debug_logfile,'a')
        fd.write("%s\n"%data)
        if datas == u"运行结束":
            data_endstr1="test start:%s, test end:%s\n"%(self.time_start,self.time_end)
            data_endstr2="total time(H):%s\n"%str(float('%0.3f'%((self.time_end-self.time_start).total_seconds()/3600)))
            fd.write(data_endstr1)
            fd.write(data_endstr2)
        fd.close()
        
        
    def outText(self,text):
        self.ui.testlog.append(text)
        #print unicode(QString(text).toUtf8(), 'utf-8', 'ignore')
        #若运行结束根据GUI控件标识自动整理报告
        self.Debug_Log(unicode(QString(text).toUtf8(), 'utf-8', 'ignore'))
        self.make_report=self.ui.make_report.isChecked()
        # if  unicode(QString(text).toUtf8(), 'utf-8', 'ignore') == u"运行结束":
            #print "aaaaaaaaaa"
            # self.time_end=datetime.datetime.now()
            # print self.time_end
        if  unicode(QString(text).toUtf8(), 'utf-8', 'ignore') == u"运行结束" and  self.make_report:
            self.make_test_report()
            
    def set_log(self):
        autodir =QFileDialog.getExistingDirectory()
        if autodir:
            self.ui.path_log.setText(unicode(autodir))
    def get_auto(self):
        autodir =QFileDialog.getExistingDirectory()
        if autodir:
            self.ui.path_auto.setText(unicode(autodir))
    def get_tcl(self):
        s=QFileDialog.getOpenFileName(self,u"查找tclsh.exe","C:/Tcl/bin","tclsh.exe(*.exe)")    
        self.ui.path_tcl.setText(unicode(s))    
    def get_python(self):
        s=QFileDialog.getOpenFileName(self,u"查找python.exe","C:/python24","python.exe(*.exe)")    
        self.ui.path_python.setText(unicode(s))
    def save_config(self):
        if not self.config:
            self.config = ConfigObj(self.configfile,encoding='UTF8')
        dir_auto=unicode(self.ui.path_auto.text())
        dir_tcl=unicode(self.ui.path_tcl.text())
        dir_python=unicode(self.ui.path_python.text())
        dir_log=unicode(self.ui.path_log.text())
        #ssid=unicode(self.ui.ssid_name.text())
        #ssid5=unicode(self.ui.ssid_name5g.text())
        product=unicode(self.ui.dut_type.currentText())
        user=unicode(self.ui.dut_user.text())
        pwd=unicode(self.ui.dut_pwd.text())
        url=unicode(self.ui.dut_ip.text())
        user_cmp=unicode(self.ui.cmp_user.text())
        pwd_cmp=unicode(self.ui.cmp_pwd.text())
        url_cmp=unicode(self.ui.cmp_ip.text())
        if not (dir_auto and dir_tcl and dir_python):
            QMessageBox.information(self,"Information",u"所需信息不能为空") 
            return;
        # if not (os.path.exists(dir_auto) and os.path.exists(dir_tcl) and os.path.exists(dir_python)):
            # QMessageBox.information(self,"Information",u"部分路径不存在") 
            # return;
        self.config['app']={}
        self.config['app']["dir_auto"]=dir_auto
        self.config['app']["dir_tcl"]=dir_tcl
        self.config['app']["dir_python"]=dir_python
        self.config['app']["dir_log"]=dir_log
        #self.config['app']["ssid"]=ssid
        self.config['app']["product"]=product
        self.config['app']["user"]=user
        self.config['app']["pwd"]=pwd
        self.config['app']["url"]=url
        self.config['app']["user_cmp"]=user_cmp
        self.config['app']["pwd_cmp"]=pwd_cmp
        self.config['app']["url_cmp"]=url_cmp
        #self.config['app']["ssid5"]=ssid5
        self.config.write()
        QMessageBox.information(self,"Information",u"保存成功") 
        self.load_config()
    # def load_config(self):
        # if os.path.exists(self.configfile):
            # self.config = ConfigObj(self.configfile,encoding='UTF8')
        # else:
            # self.config=None
            # return
        # self.ui.path_auto.setText(unicode(self.config['app']["dir_auto"]))
        # self.ui.path_tcl.setText(unicode(self.config['app']["dir_tcl"]))
        # self.ui.path_python.setText(unicode(self.config['app']["dir_python"]))
        # if not 'dir_log'  in self.config['app']:
            # self.ui.path_log.setText(os.path.join(mainpath,"results").decode("gbk"))
        # else:
            # self.ui.path_log.setText(unicode(self.config['app']["dir_log"]))
        # if "ssid" in self.config['app']:
            # self.ui.ssid_name.setText(unicode(self.config['app']["ssid"]))
        
        
        
        
        
        
        
    def load_config(self):
        global dir_auto,dir_python
        if os.path.exists(self.configfile):
            self.config = ConfigObj(self.configfile,encoding='UTF8')
        else:
            self.config=None
            return
        #print "self.config=",self.config
        self.ui.path_auto.setText(unicode(self.config['app']["dir_auto"]))
        self.ui.path_tcl.setText(unicode(self.config['app']["dir_tcl"]))
        self.ui.path_python.setText(unicode(self.config['app']["dir_python"]))
        #self.ui.dut_type.setItemText(0,unicode(self.config['app']["product"]))
        self.ui.dut_user.setText(unicode(self.config['app']["user"]))
        self.ui.dut_pwd.setText(unicode(self.config['app']["pwd"]))
        self.ui.dut_ip.setText(unicode(self.config['app']["url"]))
        self.ui.cmp_user.setText(unicode(self.config['app']["user_cmp"]))
        self.ui.cmp_pwd.setText(unicode(self.config['app']["pwd_cmp"]))
        self.ui.cmp_ip.setText(unicode(self.config['app']["url_cmp"]))
        
        if not 'dir_log'  in self.config['app']:
            self.ui.path_log.setText(os.path.join(mainpath,"results").decode("gbk"))
        else:
            self.ui.path_log.setText(unicode(self.config['app']["dir_log"]))
        # if "ssid" in self.config['app']:
            # self.ui.ssid_name.setText(unicode(self.config['app']["ssid"]))
        # if "ssid5" in self.config['app']:
            # self.ui.ssid_name5g.setText(unicode(self.config['app']["ssid5"]))              
        dir_auto=unicode(self.ui.path_auto.text())
        #print dir_auto
        GlobalVar.set_dir_auto(self.ui.path_auto.text())
        dir_python=unicode(self.ui.path_python.text())
        GlobalVar.set_dir_python(self.ui.path_python.text())
        #GlobalVar.set_dir_log(self.ui.path_log.text())
        
    def init_tree(self):
        xml_path=os.path.join(mainpath,"cases")
        #print "xml_path=",xml_path
        self.ui.casetree=CaseTreeWidget(self)
        self.ui.casetree.setGeometry(QtCore.QRect(0, 0, 341, 571))
        self.ui.casetree.setObjectName(_fromUtf8("casetree"))
        self.ui.casetree.headerItem().setText(0, _fromUtf8("1"))
        self.ui.casetree.setHeaderLabel(u"用例树");           
        self.ui.casetree.setColumnCount(1)
        self.ui.casetree.setMaximumWidth(360);
        self.root=CaseWidgetItem(self.ui.casetree)
        self.root.setText(0,u"树根");
        self.ui.casetree.setItemExpanded(self.root,True)
        xmlfiles=[i for i in os.listdir(xml_path) if os.path.splitext(i)[1]=='.xml']
        for xmlfile in xmlfiles:
            tree = ET.ElementTree(file=os.path.join(xml_path,xmlfile))
            xmlroot=tree.getroot()
            item_name=xmlroot.get("name")
            ModelTtem=CaseWidgetItem(self.root)
            ModelTtem.itype="model"
            ModelTtem.iname=item_name
            ModelTtem.setText(0,item_name)
            ModelTtem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable);  
            ModelTtem.setCheckState (0, Qt.Unchecked); 
            for child in xmlroot:
                CaseItem=TreeWidgetItem(child.get("id"),ModelTtem)
                CaseItem.itype="case"
                CaseItem.iname=child.get("name")
                CaseItem.setText(0,child.get("name"))
                CaseItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable);  
                CaseItem.setCheckState (0, Qt.Unchecked);
        self.connect(self.ui.casetree,SIGNAL("itemChanged(QTreeWidgetItem*, int)"),self.select_action)
    #*****************树形选择动作**********
    def select_action(self,item,index):
        if Qt.PartiallyChecked!=item.checkState(0):
            self.setChildCheckState(item,item.checkState(0));  
        if Qt.PartiallyChecked==item.checkState(0):
            if not self.isTopItem(item):
                item.parent().setCheckState(0,Qt.PartiallyChecked); 
    
    def setChildCheckState(self,item,cs):
        if not item:return;
        for i in range(item.childCount()):
            child=item.child(i);
            if child.checkState(0)!=cs:
                child.setCheckState(0, cs);
        self.setParentCheckState(item.parent());
    def setParentCheckState(self,item):
        if not item:return;
        selectedCount=0;
        childCount = item.childCount();
        for i in range(item.childCount()):
            child= item.child(i);
            if child.checkState(0)==Qt.Checked:
                selectedCount+=1;
        if selectedCount == 0:
            item.setCheckState(0,Qt.Unchecked);
        elif selectedCount == childCount:
            item.setCheckState(0,Qt.Checked);
        else:
            item.setCheckState(0,Qt.PartiallyChecked);
    def isTopItem(self,item):  
        if not item: return False;  
        if not item.parent(): return True;  
        return False;
    #*****************树形选择动作**********


if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()
    # SOBJ=Serial_DIY('COM8',115200)
    # SOBJ.atten_opt('ifconfig')