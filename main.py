import datetime
import os
import time
import shutil
import multiprocessing
from multiprocessing import freeze_support


def getfile(root_dir, log_file_path, allfiles=None):
    if allfiles is None:
        allfiles = {}
    files = os.listdir(root_dir)
    for file in files:
        path = root_dir + '/' + file
        if not os.path.isdir(path):
            allfiles[path] = os.stat(path).st_mtime
            with open(log_file_path, 'a', encoding='utf-8') as a:
                a.write('%s|%f\n' % (path, allfiles[path]))
        else:
            getfile(path, log_file_path)
    return allfiles


def compare_log(doc_name, update=None):
    if update is None:
        update = []
    if not os.path.exists('./log/IO-%s.txt' % doc_name):
        r = open('./log/IO-%s.txt' % doc_name, 'w')
        r.close()
    with open('./log/IO-%s.txt' % doc_name, 'r', encoding='utf-8') as r:
        txt = r.readlines()
    my_dir = {}
    for row in txt:
        (key, value) = row.split('|')
        my_dir[key] = value.replace('\n', '')
    my_dir2 = {}
    with open(setup_file_path, 'r', encoding='utf-8') as r:
        txt = r.readlines()
    for row in txt:
        (key, value) = row.split('|')
        my_dir2[key] = value.replace('\n', '')
    keys = set(list(my_dir.keys()) + list(my_dir2.keys()))
    for k in keys:
        try:
            if my_dir2[k] != my_dir[k]:
                update.append(k)
        except KeyError:
            update.append(k)
    return update


def ay_copy(from_path, to_path):
    shutil.copy(from_path, to_path)
    print('%s finished' % (os.path.basename(from_path)))


def copy_file(_to_path, _from_path, _update_dir, doc_name):
    po = multiprocessing.Pool(processes=5)
    # q = multiprocessing.Manager().Queue()
    for item in _update_dir:
        new_path = os.path.dirname(item).replace(_from_path, _to_path)
        try:
            os.makedirs(new_path)
        except PermissionError and FileExistsError:
            pass
        # shutil.copy(item, new_path)
        po.apply_async(ay_copy, (item, new_path))
    po.close()
    po.join()
    os.remove('./log/IO-%s.txt' % doc_name)
    shutil.copy(setup_file_path, os.path.join(os.path.dirname(setup_file_path), 'IO-%s.txt' % doc_name))


if __name__ == "__main__":
    try:
        freeze_support()
        print(time.process_time())
        # 创建以时间命名的日志文件并读取当前的文件状态
        if not os.path.exists('./log'):
            os.mkdir('./log')
        disk_lst = {
            'put server information here'
        }
        for key, value in disk_lst.items():
            setup_filename = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
            setup_file_path = '%s%s.txt' % ('./log/', setup_filename)
            f = open(setup_file_path, 'w', encoding='utf-8')
            f.close()
            print('start loop %s' % key)
            from_path = value[0]
            to_path = value[1]
            getfile(from_path, setup_file_path)
            print('file got!')
            print(time.process_time())
            print('start compare!')
            update_dir = compare_log(key)
            print('compare finished')
            print(time.process_time())
            print('start copy!')
            copy_file(to_path, from_path, update_dir, key)
            print(time.process_time())
            time.sleep(5)
    except Exception as ex:
        print('%s' % ex)
        time.sleep(5)
