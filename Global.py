#encoding=utf-8
#全局变量定义区域
import os,sys
#dir_auto="aaa"
#dir_python=""
class GlobalVar: 
  dir_auto = None
  dir_python = None
  dir_log = None
def set_dir_auto(db): 
  GlobalVar.dir_auto = db 
def get_dir_auto(): 
  return GlobalVar.dir_auto 
def set_dir_python(db): 
  GlobalVar.dir_python = db 
def get_dir_python(): 
  return GlobalVar.dir_python 
def set_dir_main(db): 
  GlobalVar.dir_log = db 
def get_dir_main(): 
  return GlobalVar.dir_log 
