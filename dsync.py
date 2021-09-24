import os
import hashlib
from shutil import copyfile, rmtree


def file_hash(file):                        #Finding MD5 file hash
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

def sync_dir(source_dir, clone_dir):
    base_folder,base_dirs = fill_with_files(source_dir)
    point_folder,point_dirs = fill_with_files(clone_dir)
    #STEP 1 - creating folders
    for folder in base_dirs.keys():
        if folder not in point_dirs.keys():
            os.makedirs(clone_dir + folder)
            print('Folders created: %s'%(clone_dir + folder))
            #NEEDS LOG
    
    for file in point_folder.keys():
        #STEP 2 - remove files which have different hashes
        if not file in base_folder.keys():
            #os.remove(clone_dir.join(point_folder[file]))
            os.remove(os.path.join(clone_dir +point_folder[file][0],point_folder[file][1]))
            print('File removed: %s'%os.path.join(clone_dir +point_folder[file][0],point_folder[file][1]))
            #NEEDS LOG
            continue
        #STEP 3 - check file locations and names
        if base_folder[file] != point_folder[file]:
            if not os.path.exists(clone_dir + base_folder[file][0]):
                os.makedirs(clone_dir + base_folder[file][0])
                print('Folders created2: %s'%(clone_dir + base_folder[file][0]))
                #NEEDS LOG
            os.rename(os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1]))
            print('File was moved and renamed from %s to %s'%\
                        (os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1])))
            #NEEDS LOG
            continue
    #STEP 3 - deleting folders
    for folder in point_dirs.keys():
        if folder not in base_dirs.keys() and os.path.exists(clone_dir+folder):
            rmtree(clone_dir+folder)
            print('Папки удалены: %s'%(clone_dir+folder))
            #NEEDS LOG
    #STEP 4 - copy files
    for file in base_folder.keys():
        if not file in point_folder.keys():
            copyfile(os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                    os.path.join(clone_dir +base_folder[file][0],base_folder[file][1]))
            print('Файл был скопирован из %s в %s'%\
                (os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                os.path.join(clone_dir +base_folder[file][0],base_folder[file][1])))
            #NEEDS LOG
    #NEEDS TIMER
    #NEED COMMENTS



sync_dir('/home/danil/maindir','/home/danil/clonedir')
