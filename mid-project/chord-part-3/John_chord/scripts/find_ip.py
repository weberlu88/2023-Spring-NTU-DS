
import subprocess
import msgpackrpc
import hashlib

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def hash(str):
	return int(hashlib.md5(str.encode()).hexdigest(), 16) & ((1 << 32) - 1)

filename = "a.txt"
# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")


filepath = filename
slashs = [i for i, c in list(enumerate(filepath)) if c == '/']
if len(slashs) != 0:
    filename = filename[max(slashs) + 1:]

client = new_client(my_ip, 5057)
h = hash(filename)
print("Hash of {} is {}".format(filename, h))

node = client.call("find_successor", h)
node_ip = node[0].decode()

print("a.txt should be in node:", node_ip)