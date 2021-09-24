import sys
import os
import hashlib
import time
from shutil import copyfile, rmtree
from datetime import date, datetime


def file_hash(file):                        #Функция для нахождения MD5-хэша 
    BUF_SIZE = 65536                        
    md5 = hashlib.md5()
    while True:
        data = file.read(BUF_SIZE) 
        if not data: break    
        md5.update(data)
    return md5.hexdigest()

def fill_with_files(directory):
    tmp = {}
    tmp2 = {}
    for root, dirr, files in os.walk(directory):
        tmp2[os.path.join(root).replace(directory,'')]= dirr
        for name in files:
            with open(os.path.join(root,name), 'rb') as file:
                hash = file_hash(file)
                if hash in tmp.keys():
                    hash += os.path.join(root).replace(directory,'')
                tmp[hash] = [os.path.join(root).replace(directory,''),name]
            
    return tmp,tmp2

def sync_dir(source_dir, clone_dir, log, timer=10):
    if not os.path.exists(log): 
        with open(log, 'w') as f:
            f.write('Log file started\n')
    
    base_folder,base_dirs = fill_with_files(source_dir)
    point_folder,point_dirs = fill_with_files(clone_dir)
    #STEP 1 - creating folders
    for folder in base_dirs.keys():
        if folder not in point_dirs.keys():
            os.makedirs(clone_dir + folder)
            print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + folder)))
            print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + folder)),file=open(log, "a"))
    
    for file in point_folder.keys():
        #STEP 2 - remove files which have different hashes
        if not file in base_folder.keys():
            os.remove(os.path.join(clone_dir +point_folder[file][0],point_folder[file][1]))
            print('[%s]:\tФайл удален: %s'%(datetime.now(),os.path.join(clone_dir +point_folder[file][0],point_folder[file][1])))
            print('[%s]:\tФайл удален: %s'%(datetime.now(),os.path.join(clone_dir +point_folder[file][0],point_folder[file][1])),file=open(log, "a"))
            continue
        #STEP 3 - check file locations and names
        if base_folder[file] != point_folder[file]:
            if not os.path.exists(clone_dir + base_folder[file][0]):
                os.makedirs(clone_dir + base_folder[file][0])
                print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + base_folder[file][0])))
                print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + base_folder[file][0])),file=open(log, "a"))
            os.rename(os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1]))
            print('[%s]:\tФайл был перемещен и переименован из %s в %s'%(datetime.now(),\
                        os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1])))
            print('[%s]:\tФайл был перемещен и переименован из %s в %s'%(datetime.now(),\
                        os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1])),file=open(log, "a"))
            continue
    #STEP 3 - deleting folders
    for folder in point_dirs.keys():
        if folder not in base_dirs.keys() and os.path.exists(clone_dir+folder):
            rmtree(clone_dir+folder)
            print('[%s]:\tПапки удалены: %s'%(datetime.now(),(clone_dir+folder)))
            print('[%s]:\tПапки удалены: %s'%(datetime.now(),(clone_dir+folder)),file=open(log, "a"))
    #STEP 4 - copy files
    for file in base_folder.keys():
        if not file in point_folder.keys():
            copyfile(os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                    os.path.join(clone_dir +base_folder[file][0],base_folder[file][1]))
            print('[%s]:\tФайл был скопирован из %s в %s'%(datetime.now(),\
                os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                os.path.join(clone_dir +base_folder[file][0],base_folder[file][1])))
            print('[%s]:\tФайл был скопирован из %s в %s'%(datetime.now(),\
                os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                os.path.join(clone_dir +base_folder[file][0],base_folder[file][1])),file=open(log, "a"))
    time.sleep(timer)
    sync_dir(source_dir,clone_dir,log,timer)
    #NEED COMMENTS



#sync_dir('/home/danil/maindir','/home/danil/clonedir','/home/danil/logfile')
method_name = sys.argv[1]

print(sys.argv)

getattr(sys.modules[__name__], method_name)(sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]))
