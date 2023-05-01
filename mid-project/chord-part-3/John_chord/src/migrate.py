import time
import time
import subprocess
import msgpackrpc
import hashlib
import os
import requests

dir_path = '/home/ec2-user/files'
# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")



def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def is_file_exist(filename, ip):
     
     response = requests.get("http://{}:5058/{}".format(ip, filename))
     if response.status_code == 404:
        return False
     else:
        return True

def isNeedMigrate(my_ip, filename):

    filepath = filename
    slashs = [i for i, c in list(enumerate(filepath)) if c == '/']
    if len(slashs) != 0:
        filename = filename[max(slashs) + 1:]

    client = new_client(my_ip, 5057)
    h = hash(filename)
    # print("Hash of {} is {}".format(filename, h))

    node = client.call("find_successor", h)
    node_ip = node[0].decode()

    if node_ip != my_ip: # 找到新的存放位置，要 migration
        if not is_file_exist(filename, node_ip): # 避免把備份刪除

            return node_ip
        else:
            return False
    else:
        return False

def migrate(file_name, migrate_ip):

    # migrate
    base_path = "/home/ec2-user/files/"
    simple_upload(base_path + file_name, migrate_ip)

    # delete the file
    base_path = "/home/ec2-user/files/"
    os.remove(base_path + file_name)

    print("Migrate", file_name, "to", migrate_ip, "...")

def simple_upload(filename, ip): # 參考助教 part2 test_upload.py，不用 hash 找 node，直接傳給指定 IP
    files = {
        'files': open(filename, 'rb'),
    }

    print("Uploading file to http://{}".format(ip))
    response = requests.post('http://{}:5058/upload'.format(ip), files=files)



file_list = os.listdir(dir_path)

# 定期檢查是否有檔案需要 migrate
for filename in file_list:
    migrate_ip = isNeedMigrate(my_ip, filename)

    if not migrate_ip:
        continue
    else:
        migrate(filename, migrate_ip) 
        time.sleep(3) # 避免同時太多上傳請求

# 30秒檢查一次
print("Migrate Sleep 60s ...")



