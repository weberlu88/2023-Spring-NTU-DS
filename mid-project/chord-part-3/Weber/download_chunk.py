#!/usr/bin/python3

import os
import sys
import time
import subprocess
import requests
import hashlib
import msgpackrpc
from download import download_function 

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
    return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def find_successor(alais_ip:str, id:int=1111):
    ''' test if find_successor with key id works '''
    client = new_client(alais_ip, 5057)
    try:
        node = client.call("find_successor", id)
        node_ip = node[0].decode()
        print(f"find_successor id: {id}'s successor is {node_ip}")
        return node_ip
    except:
        print(f"find_successor id: {id} failed (warning)")
        return None

def is_file_exist(filename, ip) -> bool:
    """ 向對方的 API server 確認 Filesystem 中有沒有此檔案 """
    response = requests.get(
        "http://{}:9999/file_exists?filename={}".format(ip, filename)
    )
    if response.status_code == 200:
        data = response.json()
        try:
            if data["file_exists"]:
                return True
        except:
            return False
    return False


''' main '''
'''
若欲下載的檔名為 file.txt，則先去負責的節點尋找 file.txt-part1 (也尋找 file.txt 防呆)
依序尋找 file.txt-part2, file.txt-part3 … 斷定切片有 1 ~ N 份。
下載完數個切片檔至 /chunks 資料夾再組裝起來得到 file.txt。
'''
filename = sys.argv[1]
ip = sys.argv[2]
my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
# my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")

# download file chuncks
print("download file chunks...")
numOfparts = 0
chunk_list = []
while True:
    numOfparts += 1
    chunkname = f"{filename}-part{numOfparts}"
    chunkpath = f"./chunks/{chunkname}"
    node_ip = find_successor(my_ip, hash(chunkname))
    if node_ip and is_file_exist(chunkname, node_ip):
        # 若再改進 download_function，可以省一次 find_successor()
        download_function(chunkname, node_ip, outfile=chunkpath)
        chunk_list.append(chunkpath)
    else:
        numOfparts -= 1
        break
print('parts:', chunk_list)

# build up origin big file
print("combining file chunks...")
with open(filename, 'wb') as output_file:
    for chunkpath in chunk_list:
        # 讀取 chunk 檔案
        with open(chunkpath, 'rb') as chunk_file:
            chunk_data = chunk_file.read()
        # 將 chunk 寫入輸出檔案
        output_file.write(chunk_data)
print(f'{filename} is downloaded done...\n')