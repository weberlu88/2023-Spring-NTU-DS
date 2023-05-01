import requests, sys

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

ip = sys.argv[1]
filename = sys.argv[2]

res = is_file_exist(filename, ip)
print(res, '\n')