import os
import sys
import pickle
import time
import subprocess
import requests
import hashlib
import msgpackrpc

### The code need to put into /home/ec2-user/files ##
# you can change it by specify the "dir path" into all download funciton - simple_download() and hash_download()"

### The code need to create a "lb_download dir" --> /home/ec2-user/part3/files/lb_download/

# base_path = '/home/ec2-user/part3/'
file_name = sys.argv[1]
ip = sys.argv[2]
# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")


def get_file_chunk_dict(filename, ip):
    file_path = filename + ".pkl"
    file_chunk_dict = {}

    # 取得持有檔案的 node ip
    client = new_client(ip, 5057)
    h = hash(file_path)
    # print("Hash of {} is {}".format(file_path, h))

    node = client.call("find_successor", h)
    node_ip = node[0].decode()

    # 取得 remote <filename.pkl>
    response = requests.get("http://{}:5058/{}".format(node_ip, file_path))
    if response.status_code != 404:

        with open(file_path, "wb") as f:
            f.write(response.content)

        with open( file_path, 'rb') as f:
            file_chunk_dict = pickle.load(f)

        os.remove(file_path) # download 的本地端不用存

        return file_chunk_dict

    else:
        return False


def simple_download(filename, ip): # 參考助教 part2 test_download.py，不用 hash 找 node，直接從指定 IP 下載
    print("Downloading file from http://{}".format(ip))
    response = requests.get("http://{}:5058/{}".format(ip, filename))

    with open(filename, "wb") as f:
        f.write(response.content)

def hash_download(filename, ip): # 參考助教 part2 download.py

    client = new_client(ip, 5057)
    h = hash(filename)
    print("Hash of {} is {}".format(filename, h))

    node = client.call("find_successor", h)
    node_ip = node[0].decode()

    print("Downloading file from http://{}".format(node_ip))
    response = requests.get("http://{}:5058/{}".format(node_ip, filename))

    with open(filename, "wb") as f:
        f.write(response.content)

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def rm_file(file_path):
    try:
        # 刪除檔案
        os.remove(file_path)
        print(f"{file_path} 檔案已刪除")
    except Exception as e:
        print(f"刪除 {file_path} 檔案時發生錯誤：{str(e)}")

def lb_download(file_name, ip, file_chunk_dict):


    num_of_chunk = file_chunk_dict["chunk_num"]
    file_chunk_path_list = []

    # 取得各個 file chunk
    for i in range(num_of_chunk):
        chunk_path = file_name + "-part-" + str(i)
        file_chunk_path_list.append(chunk_path)
        hash_download(chunk_path, ip)
        time.sleep(3)

    # 組合切分後的檔案，存在 /home/ec2-user/part3/files/lb_download/，方便確認
    folder_name = "lb_download"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    output_path = "./lb_download/" + file_name
    print("Combining file chunks......")
    with open(output_path, 'wb') as output_file:
        for file_path in file_chunk_path_list:
            # 讀取 chunk 檔案
            with open(file_path, 'rb') as chunk_file:
                chunk_data = chunk_file.read()
            
            # 將 chunk 寫入輸出檔案
            output_file.write(chunk_data)

    # locally remove redundant files
    for file_path in file_chunk_path_list:
        rm_file(file_path)


### main() ###
file_chunk_dict = get_file_chunk_dict(file_name, ip)
print("file_chunk_dict:", file_chunk_dict)

# 判斷檔案是否有被切割過 
if file_chunk_dict:
    print("Load balance download...")
    lb_download(file_name, ip, file_chunk_dict)
else:
    print("Normal download...")
    hash_download(file_name, ip)   

# if file_name in chunk_file_list:
#     print("Load balance download...")
#     lb_download(file_name, ip, my_ip)
# else:
#     print("Normal download...")
#     hash_download(file_name, ip)