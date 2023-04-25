import os
import sys
import pickle
import time
import subprocess
import requests

### The code need to put into /home/ec2-user/files ##
# you can change it by specify the "dir path" into all download funciton - simple_download() and hash_download()"

### The code need to create a "lb_download dir" --> /home/ec2-user/part3/files/lb_download/

# base_path = '/home/ec2-user/part3/'
file_name = sys.argv[1]
ip = sys.argv[2]
my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')

def get_chunk_file_namelist(ip):
    filename = 'chunk_file_list.pkl'
    chunk_file_list = []

    # 如果本地端已經有 chunk_file_list.pkl
    if os.path.exists('chunk_file_list.pkl'):
        with open( 'chunk_file_list.pkl', 'rb') as f: # 先讀取現有的檔案
            chunk_file_list = pickle.load(f)

            return chunk_file_list
    # 沒有就跟 remote 端拿
    else:
        try:
            # print("simple download:", filename, ip)
            # simple_download(filename, ip)
            response = requests.get("http://{}:5058/{}".format(ip, filename))

            with open('chunk_file_list.pkl', "wb") as f:
                f.write(response.content)

            with open( 'chunk_file_list.pkl', 'rb') as f: 
                chunk_file_list = pickle.load(f)

            os.remove('chunk_file_list.pkl') # download 的本地端不用存
            
            return chunk_file_list
            
        except Exception as e:
            print("File Not Found:", filename)
            return chunk_file_list
    
    return chunk_file_list
def get_chunk_dict(filename, ip):
    file_path = filename + ".pkl"
    file_chunk_dict = {}

    if os.path.exists(file_path):
        with open( file_path, 'rb') as f: # 先讀取現有的檔案
            file_chunk_dict = pickle.load(f)

            return file_chunk_dict
    else:
        # 取得 remote <filename.pkl>
        response = requests.get("http://{}:5058/{}".format(ip, file_path))
        with open(file_path, "wb") as f:
            f.write(response.content)

        with open( file_path, 'rb') as f:
            file_chunk_dict = pickle.load(f)

        os.remove(file_path) # download 的本地端不用存

        return file_chunk_dict

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

def lb_download(file_name, ip, my_ip):
    dict_path = file_name + '.pkl'
    file_chunk_dict = get_chunk_dict(file_name, ip)
    print("chunk_dict:", file_chunk_dict)
    
    file_path_list = list(file_chunk_dict.values())

    for ip in file_chunk_dict:
        if ip != my_ip: # 如果本地端沒有
            # 從各個 node 下載檔案
            simple_download(file_chunk_dict[ip], ip)
            time.sleep(5)

    # 組合切分後的檔案，存在 /home/ec2-user/part3/files/lb_download/，方便確認
    folder_name = "lb_download"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    output_path = "./lb_download/" + file_name
    print("Combining file chunks......")
    with open(output_path, 'wb') as output_file:
        for file_path in file_path_list:
            # 讀取 chunk 檔案
            with open(file_path, 'rb') as chunk_file:
                chunk_data = chunk_file.read()
            
            # 將 chunk 寫入輸出檔案
            output_file.write(chunk_data)

    # locally remove redundant files
    for ip in file_chunk_dict:
        if ip != my_ip:
            rm_file(file_chunk_dict[ip])


### main() ###
chunk_file_list = get_chunk_file_namelist(ip)
print("chunk_file_list:", chunk_file_list)

# 判斷檔案是否有被切割過 # file name 或許改成 hash value 會比較好?

if file_name in chunk_file_list:
    print("Load balance download...")
    lb_download(file_name, ip, my_ip)
else:
    print("Normal download...")
    hash_download(file_name, ip)