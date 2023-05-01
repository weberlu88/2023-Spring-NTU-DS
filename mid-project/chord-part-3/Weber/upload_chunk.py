import os
import sys
import requests
import msgpackrpc
import hashlib
import time
import subprocess
from upload import upload_function

def get_filename_from_path(filepath:str) -> str:
    ''' /user/a.txt >> a.txt '''
    filename = filepath
    slashs = [i for i, c in list(enumerate(filepath)) if c == '/']
    if len(slashs) != 0:
        filename = filename[max(slashs) + 1:]
    return filename

def split_file_to_chunk(filepath, file_size, chunk_size) -> list:
    ''' /user/a.txt >> [chunks/a.txt-part1, chunks/a.txt-part2] '''
    # 計算每個切分後的檔案大小, 數量
    filename = get_filename_from_path(filepath)
    num_chunks = file_size // chunk_size + 1  # 6Mb = 4 + 2
    chunk_sizes = [chunk_size] * num_chunks

    # 如果還有剩餘的 bytes，分配到最後一個 chunk
    if file_size % chunk_size != 0:
        chunk_sizes[-1] = file_size % chunk_size

    # print("chunk_sizes",chunk_sizes)

    # cut file
    os.makedirs("./chunks", exist_ok=True)
    chunk_path_list = []
    with open(filepath, 'rb') as f:
        for i in range(num_chunks):
            # 從 f 物件往後讀取 chunk_size 個 bytes
            chunk_data = f.read(chunk_sizes[i])

            # 確定 chunk 檔案的路徑
            chunk_path = f"./chunks/{filename}-part{i+1}"
            chunk_path_list.append(chunk_path)

            # 寫入 chunk 檔案
            with open(chunk_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            print(chunk_path, f"{chunk_sizes[i]//(1024*1024)}MB")
    return chunk_path_list

def remove_files():
    dir_path = "./chunks"
    files = os.listdir(dir_path)
    for file in files:
        # construct full file path
        file_path = os.path.join(dir_path, file)
        try:
            # delete the file
            os.remove(file_path)
            # print(f"{file_path} has been deleted.")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

''' main script '''
'''
若欲上傳的檔案大小大於 4 MB (file.txt)，則先在本地被切成多個 4 MB 以及1個 0~4 MB 的剩餘檔案，
將新增的切片檔案命名為 file.txt-part1, file.txt-part2, … , file.txt-partN
'''

filepath = sys.argv[1]
ip = sys.argv[2]
# filename = get_filename_from_path(filepath)
file_size = os.path.getsize(filepath) # unit = bytes
threshold = 1024*1024*4 # 4 MB

my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8') # private
# my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n") # public

print("File size:", file_size, "Threshold:", threshold)
if file_size > threshold:
    print("Need to cut file...")
    chunk_path_list = split_file_to_chunk(filepath, file_size, threshold)
    print("chunk_path_list:", chunk_path_list)
    for p in chunk_path_list:
        upload_function(p, ip)
    remove_files()
else:
    print("Simple upload...")
    upload_function(filepath, ip)