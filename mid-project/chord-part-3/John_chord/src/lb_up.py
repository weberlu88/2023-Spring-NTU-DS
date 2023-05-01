import os
import sys
import requests
import msgpackrpc
import hashlib
import pickle
import time
import subprocess

file_name = sys.argv[1]
ip = sys.argv[2]
file_size = os.path.getsize(file_name) # unit = bytes
threshold = 1024*1024*10 # 10MB

# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")




def is_alive_node(targer_ip):
    client = new_client(targer_ip, 5057)
    try:
        c_info = client.call("get_info")
        print("c_info:", c_info, "type:", type(c_info))
        successor = client.call("get_successor", 0)
        print("successor:", successor)
        if successor[0] == b'':
            return False
    except Exception as e:
        print("Non-alive node:", targer_ip)
        return False
    
    return True
    
def rm_file(file_path):
    try:
        # 刪除檔案
        os.remove(file_path)
        print(f"{file_path} 檔案已刪除")
    except Exception as e:
        print(f"刪除 {file_path} 檔案時發生錯誤：{str(e)}")

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

    node = client.call("find_successor", h)
    node_ip = node[0].decode()

    files = {
        'files': open(filepath, 'rb'),
    }

    print("Uploading file to http://{}".format(node_ip))
    response = requests.post('http://{}:5058/upload'.format(node_ip), files=files)

    return node_ip

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

def lb_upload(file_name, file_size, ip):

    file_chunk_dict = {} # {"chunk_num": x}

    # 計算每個切分後的檔案大小, 數量
    chunk_size = 1024*1024*2 # 2MB # 最多設定 2MB 因為剩餘沒切乾淨可能是 1.9999MB 加起來才不會超過 4 MB
    num_chunks = file_size // chunk_size
    chunk_sizes = [chunk_size] * num_chunks
    file_chunk_dict["chunk_num"] = num_chunks

    # 如果還有剩餘的 bytes，分配到最後一個 chunk
    if file_size % num_chunks != 0:
        chunk_sizes[-1] += file_size % num_chunks

    print("chunk_sizes:", chunk_sizes)

    # cut file to chunk-part-1, chunk-part-2, chunk-part-3...
    with open(file_name, 'rb') as f:
        for i in range(num_chunks):
            # 讀取 chunk_size 個 bytes
            chunk_data = f.read(chunk_sizes[i])

            # 確定 chunk 檔案的路徑
            chunk_path = file_name + "-part-" + str(i)

            # 寫入 chunk 檔案
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)    

    # 儲存資訊 {"chunk_num": x}
    with open(file_name + '.pkl', 'wb') as f:
        pickle.dump(file_chunk_dict, f)   

    # 上傳 file chunk
    upload_info = {}
    for i in range(num_chunks):
        chunk_path = file_name + "-part-" + str(i)
        node_ip = hash_upload(chunk_path, ip)
        if node_ip not in upload_info:
            upload_info[node_ip] = [chunk_path]
        else:
            upload_info[node_ip].append(chunk_path)

        time.sleep(3)

        # 刪除本地端的 file chunk
        rm_file(chunk_path)
    
    # 上傳 metadata {"chunk_num": x}
    hash_upload(file_name + '.pkl', ip)
    rm_file(file_name + '.pkl') # 刪除本地端的 metadata
    
    return upload_info

### main() ###
print("File size:", file_size, "Threshold:", threshold)
if file_size > threshold:
    print("Load balance upload...")
    upload_record = lb_upload(file_name, file_size, ip) # a directory 
    print("Upload detail:", upload_record)
    
else:
    upload_ip = hash_upload(file_name, ip)
    print("Normal upload to:", upload_ip)
    

