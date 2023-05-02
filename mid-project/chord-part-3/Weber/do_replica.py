import os
import msgpackrpc
import time
import subprocess
import requests
import hashlib
import random


def new_client(ip, port):
    return msgpackrpc.Client(msgpackrpc.Address(ip, port))


def hash(str):
    return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)


def simple_upload(file_name, ip):
    """Upload fuction from TA"""
    base_path = "/home/ec2-user/files/"
    files = {
        "files": open(base_path + file_name, "rb"),
    }

    print("Uploading file to http://{}".format(ip))
    response = requests.post("http://{}:5058/upload".format(ip), files=files)


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


def set_replica(filename, my_ip):
    ''' 當 filename 為自己負責的，檢查後2個successor的備份，沒有則補上 '''
    client = new_client(my_ip, 5057)

    # successor 1
    node_s1 = client.call("get_successor", 0)
    node_s1_ip = node_s1[0].decode()

    if node_s1_ip != my_ip:
        if not is_file_exist(filename, node_s1_ip):  # 如果沒有 replica 才需要放新的 replica
            print("Set replica to:", node_s1_ip, "File:", filename)
            simple_upload(filename, node_s1_ip)

    # successor 2
    node_s2 = client.call("get_successor", 1)
    node_s2_ip = node_s2[0].decode()

    if node_s2_ip != my_ip:
        if not is_file_exist(filename, node_s2_ip):
            print("Set replica to:", node_s2_ip, "File:", filename)
            simple_upload(filename, node_s2_ip)

''' main script '''
dir_path = "/home/ec2-user/files"
# my_ip = (
#     subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"])
#     .decode("utf-8")
#     .strip("\n")
# ) # public
my_ip = subprocess.check_output(
    ["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]
).decode("utf-8") # private

print("replica: Start.")
file_list = os.listdir(dir_path)
print("file_list:", file_list)

if len(file_list) > 0:
    # check all the file if any file is hosted by this node 
    # (If the node is first node, it host the file)
    for filename in file_list:
        # get the filename hash
        filepath = filename
        slashs = [i for i, c in list(enumerate(filepath)) if c == "/"]
        if len(slashs) != 0:
            filename = filename[max(slashs) + 1 :]
        h = hash(filename)

        # check if the node is the first node
        client = new_client(my_ip, 5057)
        node = client.call("find_successor", h)
        node_ip = node[0].decode()

        if node_ip == my_ip:  # I'm the first replica node
            set_replica(filename, my_ip)  # set replica to other node
            time.sleep(random.uniform(0, 4))

else:
    print("No any files... ", end="")

print("replica: end.")