import sys
import os
import hashlib
import time
from shutil import copyfile, rmtree
from datetime import date, datetime


def file_hash(file):                        #Функция для нахождения MD5-хэша
    BUF_SIZE = 65536                        #Вводим константу, на случай большого размера файла
    md5 = hashlib.md5()                     
    while True:                             #Читаем файл блоками, чтобы не нагружать оперативную память
        data = file.read(BUF_SIZE) 
        if not data: break    
        md5.update(data)
    return md5.hexdigest()                  #Возвращаем найденый хэш

def fill_with_files(directory):             #Функция для заполнения словаря по принципу HASH:LOCATION
    tmp = {}
    tmp2 = {}                               #Дополнительная переменная используется для обнаружения пустых дирректорий
    for root, dirr, files in os.walk(directory):
        tmp2[os.path.join(root).replace(directory,'')]= dirr
        for name in files:
            with open(os.path.join(root,name), 'rb') as file:
                hash = file_hash(file)      #Если в папках несколько одинаковых файлов, в разных локациях или с разными именами
                if hash in tmp.keys():      #То в словарь попадет только последний хэш. Поэтому мы вводим проверку на наличие хэша в сорваре
                    hash += os.path.join(root).replace(directory,'')    #И если он уже там мы прибавляем к хэшу локацию, таким образом все файлы попадут в словарь, даже дубликаты
                tmp[hash] = [os.path.join(root).replace(directory,''),name]
    return tmp,tmp2

def sync_dir(source_dir, clone_dir, log, timer=10):     #Основная функция синхронизации дирректорий
    if not os.path.exists(log):                         #Создаем файл логов
        with open(log, 'w') as f:
            f.write('Log file started\n')
    
    base_folder,base_dirs = fill_with_files(source_dir) #Получаем словарь HASH:FILE и словарь необходимый для выявления пустых папок в осноновной дирректории
    point_folder,point_dirs = fill_with_files(clone_dir)#Делаем аналогичную работу для каталога-реплики
        #ШАГ 1 - Мы создаем недостающие папки в каталоге-реплике
    for folder in base_dirs.keys():
        if folder not in point_dirs.keys():
            os.makedirs(clone_dir + folder)
            #LOG
            print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + folder)))
            print('[%s]:\tПуть создан: %s'%(datetime.now(),(clone_dir + folder)),file=open(log, "a"))
    
    for file in point_folder.keys():
        #ШАГ 2 - если в каталоге-реплике присутствует файл, которого нет в оригинале - мы удаляем этот файл.
        if not file in base_folder.keys():
            os.remove(os.path.join(clone_dir +point_folder[file][0],point_folder[file][1]))
            #LOG
            print('[%s]:\tФайл удален: %s'%(datetime.now(),os.path.join(clone_dir +point_folder[file][0],point_folder[file][1])))
            print('[%s]:\tФайл удален: %s'%(datetime.now(),os.path.join(clone_dir +point_folder[file][0],point_folder[file][1])),file=open(log, "a"))
            continue
        #ШАГ 3 - Если в каталоге-реплике навести немного суеты и переименовать, а так же переместить некоторые файлы
        #то благодаря словарю с хэшами мы можем восстановить порядок, аналогичный тому, что есть в основном каталоге
        if base_folder[file] != point_folder[file]:
            #Проверка на существование дирректории здесь не нужна, ведь мы уже создали все папки в ШАГ 1
            os.rename(os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1]))
            #LOG
            print('[%s]:\tФайл был перемещен и переименован из %s в %s'%(datetime.now(),\
                        os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1])))
            print('[%s]:\tФайл был перемещен и переименован из %s в %s'%(datetime.now(),\
                        os.path.join(clone_dir+point_folder[file][0],point_folder[file][1]),
                        os.path.join(clone_dir+base_folder[file][0],base_folder[file][1])),file=open(log, "a"))
            continue
        #ШАГ 4 - Если в каталоге-реплике создали папки, которых не существует в основном каталоге, то мы их удаляем 
    for folder in point_dirs.keys():
        if folder not in base_dirs.keys() and os.path.exists(clone_dir+folder):
            rmtree(clone_dir+folder)
            #LOG
            print('[%s]:\tПапки удалены: %s'%(datetime.now(),(clone_dir+folder)))
            print('[%s]:\tПапки удалены: %s'%(datetime.now(),(clone_dir+folder)),file=open(log, "a"))
    #ШАГ 5 - наконец мы копируем только недостающие файлы
    for file in base_folder.keys():
        if not file in point_folder.keys():
            copyfile(os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                    os.path.join(clone_dir +base_folder[file][0],base_folder[file][1]))
            #LOG
            print('[%s]:\tФайл был скопирован из %s в %s'%(datetime.now(),\
                os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                os.path.join(clone_dir +base_folder[file][0],base_folder[file][1])))
            print('[%s]:\tФайл был скопирован из %s в %s'%(datetime.now(),\
                os.path.join(source_dir +base_folder[file][0],base_folder[file][1]),
                os.path.join(clone_dir +base_folder[file][0],base_folder[file][1])),file=open(log, "a"))
    time.sleep(timer)   #И перезапускаем функцию через время указанное пользователем в секундах.
    sync_dir(source_dir,clone_dir,log,timer)

#Принимаем значения метода sync_dir() из терминала
getattr(sys.modules[__name__], 'sync_dir')(sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]))
