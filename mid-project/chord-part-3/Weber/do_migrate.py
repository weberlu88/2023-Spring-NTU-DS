import time
import time
import subprocess
import msgpackrpc
import hashlib
import os
import requests
import random

def new_client(ip, port):
    return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
    return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

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

def isNeedMigrate(origin_ip, filename) -> str:
    """hash the filename as key, and find successor of the key.
    If successor is not origin_ip, return new ip for the filename."""

    filepath = filename
    slashs = [i for i, c in list(enumerate(filepath)) if c == "/"]
    if len(slashs) != 0:
        filename = filename[max(slashs) + 1 :]

    client = new_client(origin_ip, 5057)
    h = hash(filename)
    print("migrate::isNeedMigrate: Hash of {} is {}".format(filename, h))

    try:
        node = client.call("find_successor", h)
        node_ip = node[0].decode()
    except:
        print(f"migrate::isNeedMigrate: fail to find {filename}'s successor")
        return False

    print("Upload IP:", node_ip)
    print("My IP:", origin_ip)

    if node_ip != origin_ip and is_file_exist(filename, node_ip) == False:  
        # 找到新的存放位置，要 migration
        return node_ip
    else:
        return False

def migrate(file_name, migrate_ip):
    ''' upload(post) and delete local file '''
    # migrate
    base_path = "/home/ec2-user/files/"
    simple_upload(base_path + file_name, migrate_ip)

    # delete the file
    # base_path = "/home/ec2-user/files/"
    # os.remove(base_path + file_name)

    print("Migrate", file_name, "to", migrate_ip, "...")

def simple_upload(filename, ip):
    """助教 part2 test_upload.py，直接傳給指定 IP"""
    files = {
        "files": open(filename, "rb"),
    }

    print("Uploading file to http://{}".format(ip))
    response = requests.post("http://{}:5058/upload".format(ip), files=files)


"""
* 由 crontab 每分鐘執行此檔案
檢查一次 /files 底下的所有檔案，是否有檔案需要搬動 (hash(filename) -> findsuccessor -> succ_ip)，
如果需要搬動則上傳該檔案至 succ_ip，刪除自己本地的檔案，
避免請求同時發出每上傳一個檔案會 sleep 幾秒。
"""

# 檢查所有檔案
dir_path = "/home/ec2-user/files"
my_ip = subprocess.check_output(
    ["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]
).decode("utf-8")

file_list = os.listdir(dir_path)

for filename in file_list:

    migrate_ip = isNeedMigrate(my_ip, filename) # 檔案需要 migrate 嗎

    if not migrate_ip:
        continue
    else:
        migrate(filename, migrate_ip)
        rs = random.uniform(0, 4)
        time.sleep(rs)  # 避免同時上傳
