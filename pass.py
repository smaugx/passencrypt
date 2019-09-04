#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
import base64
import sys
import pdb
import argparse

original_pass_file = '/etc/.CaoCao.data'
encrypt_pass_file  = '/etc/.CaoCao.encrypt'

# each line as one item
pass_cache = []

def encrypt(line):
    #now use base64
    new_line = base64.b64encode(line)
    return new_line

def decrypt(line):
    new_line = base64.b64decode(line)
    return new_line


# should only done once and nerver use
def encode_from_original_file():
    global original_pass_file, encrypt_pass_file
    if not os.path.exists(original_pass_file):
        print("error original file not exist")
        return False
    if os.path.exists(encrypt_pass_file):
        print("error, no need reinit")
        return False
    status = False
    fenc, fori = None, None
    try:
        fenc = open(encrypt_pass_file, 'wb')
        fori = open(original_pass_file, 'rb')
        for line in fori.readlines():
            print(line)
            new_line = encrypt(line) 
            print(new_line)
            fenc.write(new_line)
            fenc.write(b'\n')
        status = True
    except Exception as e:
        print("Exception: {0}".format(e))
    finally:
        if fenc:
            fenc.close()
        if fori:
            fori.close()
    return status
    

# load to cache from encrypt_pass_file
def load_encrypt_cache():
    global encrypt_pass_file, pass_cache
    if not os.path.exists(encrypt_pass_file):
        print("pass file not exist")
        return False
    with open(encrypt_pass_file, 'rb') as fin:
        for line in fin.readlines():
            new_line = decrypt(line)
            pass_cache.append(new_line)
    fin.close()
    return True

def show_pass(pattern = b'all'):
    global pass_cache
    if not load_encrypt_cache():
        return False
    if not pass_cache:
        print('nothing pass stored')
        return

    found_pass = []
    for line in pass_cache:
        if pattern == b'all':
            found_pass.append(line)
        elif line.find(pattern) != -1:
            found_pass.append(line)
    if not found_pass:
        print('nothing pass found')
        return
    print("found {0} maybe match\n".format(len(found_pass)))
    for line in found_pass:
        line = line.decode('utf8')
        if line[-1] == '\n':
            line = line[:-1]
        if not line:
            continue
        print("[{0}]".format(line))
    return

def add_pass(line):
    global pass_cache
    if not line:
        return False
    load_encrypt_cache()
    
    # bytes
    pass_cache.append(line)
    return True

# after add action, dump to encrypt_pass_file
def dump_pass_cache_to_encrypt_pass_file():
    global encrypt_pass_file, pass_cache
    if not pass_cache:
        print('nothing to store')
        return False
    with open(encrypt_pass_file, 'wb') as fout:
        for line in pass_cache:
            new_line = encrypt(line)
            fout.write(new_line)
            fout.write(b'\n')
    fout.close()
    return True

# after add action, dump to original_pass_file 
def dump_pass_cache_to_original_pass_file():
    global pass_cache, original_pass_file
    if not pass_cache:
        print('nothing to store')
        return False
    with open(original_pass_file, 'wb') as fout:
        for line in pass_cache:
            #new_line = line.decode('utf8')
            new_line = line
            fout.write(new_line)
            fout.write(b'\n')
    fout.close()
    return True




if __name__ == '__main__':
    version = int(sys.version_info.major)
    if version < 3:
        print("python at least version 3.x")
        sys.exit()
    parser = argparse.ArgumentParser()
    parser.description='这个工具用来很方便的管理和隐藏个人的密码'
    parser.add_argument('pow', type=int, help='login token')
    parser.add_argument('-e', '--encode', help='encode from original file, should only run one time')
    parser.add_argument('-s', '--show', help="show passowrd match pattern")
    parser.add_argument('-a', '--add', help="add password")
    args = parser.parse_args()
    if args.pow != 6969:
        print("沙雕,你看不了")
        sys.exit()

    if args.encode:
        status = encode_from_original_file()
        if status:
            print("OK")
        sys.exit()

    if args.show:
        pattern = args.show
        show_pass(pattern.encode('utf8'))
        sys.exit()

    if args.add:
        line = args.add
        add_pass(line.encode('utf8'))
        status = dump_pass_cache_to_encrypt_pass_file()
        if status:
            # 可以选择要不要同步可视的密码到文件
            dump_pass_cache_to_original_pass_file()
            print("OK")
        sys.exit()
