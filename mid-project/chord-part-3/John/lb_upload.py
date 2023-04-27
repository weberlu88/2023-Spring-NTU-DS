import os
import sys
import requests
import msgpackrpc
import hashlib
import pickle
import time
import subprocess
import boto3

### The code need to put into /home/ec2-user/files ###
# you can change it by specify the "dir path" into all upload funciton - simple_upload() and hash_upload()"

# base_path = '/home/ec2-user/part3/'
file_name = sys.argv[1]
ip = sys.argv[2]
file_size = os.path.getsize(file_name) # unit = bytes
threshold = 1024*1024*100 # 100MB

my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')

def get_ec2_ips(is_including_self=True): # including self ip?
    ec2_ip = []
    ec2 = boto3.client('ec2', region_name='us-east-1')
    response = ec2.describe_instances()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'PrivateIpAddress' in instance: # if the EC2 is terminated, it will not have the private ip
                # print("instance:", instance, "\n\n")
                if is_including_self:
                    ec2_ip.append(instance['PrivateIpAddress'])
                else:
                    if instance['PrivateIpAddress'] != my_ip:
                        ec2_ip.append(instance['PrivateIpAddress'])

    return ec2_ip

def is_alive_node(targer_ip):
    client = new_client(targer_ip, 5057)
    try:
        c_info = client.call("get_info")
        if c_info[0] != b'':
            print("alive node ", "ip:", c_info[0], "type:", type(c_info[0]))
        else:
            return False
    except Exception as e:
        print("Non-alive node:", targer_ip)
        return False
    
    return True

def get_node_ips():  
    ec2_ips = get_ec2_ips(is_including_self=True) # 因為 chunk 要平均分配給所有 node，包含自己
    node_ips = []
    for ip in ec2_ips:
        if(is_alive_node(ip)):
            node_ips.append(ip)

    return node_ips
    
def rm_file(file_path):
    try:
        # 刪除檔案
        os.remove(file_path)
        print(f"{file_path} 檔案已刪除")
    except Exception as e:
        print(f"刪除 {file_path} 檔案時發生錯誤：{str(e)}")
    

def record_chunk_file_namelist(file_name):
    chunk_file_list = []

    if os.path.exists('chunk_file_list.pkl'):
        with open( 'chunk_file_list.pkl', 'rb') as f: # 先讀取現有的檔案
            chunk_file_list = pickle.load(f)      
    if file_name not in chunk_file_list:
        chunk_file_list.append(file_name) # 加入新的的檔案

    with open( 'chunk_file_list.pkl', 'wb') as f: 
        pickle.dump(chunk_file_list, f)

    return chunk_file_list

def simple_upload(file_name, ip): # 參考助教 part2 test_upload.py，不用 hash 找 node，直接傳給指定 IP
    files = {
        'files': open(file_name, 'rb'),
    }

    print("Uploading file to http://{}".format(ip))
    response = requests.post('http://{}:5058/upload'.format(ip), files=files)

def hash_upload(filename, ip): # 參考助教 part2 upload.py
    filepath = filename
    slashs = [i for i, c in list(enumerate(filepath)) if c == '/']
    if len(slashs) != 0:
        filename = filename[max(slashs) + 1:]

    client = new_client(ip, 5057)
    h = hash(filename)
    print("Hash of {} is {}".format(filename, h))

    node = client.call("create",)
    node = client.call("find_successor", h)
    node_ip = node[0].decode()

    files = {
        'files': open(filepath, 'rb'),
    }

    print("Uploading file to http://{}".format(node_ip))
    response = requests.post('http://{}:5058/upload'.format(node_ip), files=files)

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def lb_upload(file_name, file_size):

    # record the chunk file name to a list 
    chunk_file_list = record_chunk_file_namelist(file_name)
    print("chunk_file_namelist:", chunk_file_list)

    # 一些參數
    # file_path = base_path + file_name
    node_ips = get_node_ips() # like [172.165.0.1, 172.165.0.2, .172.165.0.3]
    print(node_ips)

    num_chunks = len(node_ips)
    file_chunk_dict = {}

    # 計算每個切分後的檔案大小
    chunk_size = file_size // num_chunks
    chunk_sizes = [chunk_size] * num_chunks

    # 如果還有剩餘的 bytes，分配到最後一個 chunk
    if file_size % num_chunks != 0:
        chunk_sizes[-1] += file_size % num_chunks

    print("chunk_sizes:", chunk_sizes)

    # cut_chunk and write to /home/ec2-user/part3/chunk/ # no, 因為 upload 後都會在 /files/ 裡面，不好改位置
    with open(file_name, 'rb') as f:
        for i in range(num_chunks):
            # 讀取 chunk_size 個 bytes
            chunk_data = f.read(chunk_sizes[i])

            # 確定 chunk 檔案的路徑
            # chunk_path = base_path + "chunk/" + file_name + "-part-" + str(i)
            chunk_path = file_name + "-part-" + str(i)

            # 寫入 chunk 檔案
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)    

            # 儲存資訊 ip:path
            file_chunk_dict[node_ips[i]] = chunk_path

    # 儲存資訊 ip:path to /home/ec2-user/part3/pkl/ # no, 因為 upload 後都會在 /files/ 裡面，不好改位置
    # with open(base_path + "pkl/" + file_name + '.pkl', 'wb') as f:
    with open(file_name + '.pkl', 'wb') as f:
        pickle.dump(file_chunk_dict, f)   

    # really upload the data
    for ip in file_chunk_dict:

        if ip != my_ip:
            # upload chunk data
            simple_upload(file_chunk_dict[ip] ,ip)
            time.sleep(5)
            # upload the metadata
            simple_upload('chunk_file_list.pkl', ip) # /home/ec2-user/files/chunk_file_list.pkl
            time.sleep(5)
            simple_upload(file_name + '.pkl', ip) # /home/ec2-user/files/<file_name>.pkl

    # locally remove redundant files
    for ip in file_chunk_dict:
        if ip != my_ip:
            rm_file(file_chunk_dict[ip])
    
    # rm_file(file_name)

    return file_chunk_dict

### main() ###
print("File size:", file_size, "Threshold:", threshold)
if file_size > threshold:
    print("Load balance upload...")
    upload_record = lb_upload(file_name, file_size) # a directory 
    print("Upload detail:", upload_record)
    
else:
    print("Simple upload to:", upload_ip)
    upload_ip = hash_upload(file_name, ip)
    


