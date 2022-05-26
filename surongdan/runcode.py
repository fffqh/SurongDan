
# -*- coding: utf-8 -*-
import os
import shutil
from flask import current_app
import base64
import json

# import multiprocessing
# import threading

fileacc  = "acc.jpg"
fileloss = "loss.jpg" 
filelog = "log.txt"
logpath = "log"
picpath = "pic"
filetrain = "train.py"

class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)

# a long time task 
def runcode(outpath,current_proid,current_uid):
  path1 = os.path.join(outpath,filetrain)
  path2 = os.path.join(outpath,logpath)
  path3 = os.path.join(outpath,picpath)

  pathacc = os.path.join(path3,fileacc)
  pathloss = os.path.join(path3,fileloss)
  if os.path.exists(path2):
    shutil.rmtree(path2) # 清除所有内容
  if os.path.exists(path3):
    shutil.rmtree(path3)
  # if not os.path.exists(path2):
  os.makedirs(path2)

  path2 = os.path.join(path2,filelog)
  # windows使用出现问题，可在powershell使用，flask shell未知
  cmd = "python "+ path1 +" 2>&1 | tee "+ path2
  print(cmd)
  os.system(command=cmd)
  if os.path.exists(path2) and os.path.exists(pathacc) and os.path.exists(pathloss):
    return 1 # all exist
  elif os.path.exists(path2) and (os.path.exists(pathacc) and os.path.exists(pathloss))==False:
    return 2 # picture not exists totally

  # proj_pro = project_table.query.filter(
  #     and_(project_table.project_id == current_proid, project_table.project_user_id == current_uid)).one_or_none()
 
  # with db.auto_commit_db():
  #     proj_pro.project_status = "done"

def getpic(pic):
  f=open(pic,'rb') 
  new_image_string=base64.b64encode(f.read())
  return new_image_string

def gettxt(txt):
  f = open(txt,encoding="utf8")
  return f.read()

def getoutput(outpath):
  path1 = os.path.join(outpath,filetrain)
  path2 = os.path.join(outpath,logpath,filelog)
  path3 = os.path.join(outpath,picpath)
  pathacc = os.path.join(path3,fileacc)
  print(pathacc)
  pathloss = os.path.join(path3,fileloss)
  code = ""
  log  = ""
  acc = ""
  loss = ""
  if os.path.exists(path1)==True:
    code = gettxt(path1)
  if os.path.exists(path2)==True:
    log = gettxt(path2)   
  if os.path.exists(pathacc):
    acc = getpic(pathacc)
  if os.path.exists(pathloss):
    loss = getpic(pathloss)

  # acc.encode("utf-8")
  # loss.encode("utf-8")
  print(type(code))
  print(type(acc))
  acc = json.dumps({'acc': acc}, cls=BytesEncoder)
  loss = json.dumps({'loss': loss}, cls=BytesEncoder)
  return code,log,acc,loss

if __name__ == '__main__':
    # try:
    runcode("./out")
    # except:
    #     log.logger.error("错误:%s", traceback.format_exc())

