import subprocess
import msgpackrpc

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))


# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")
client = new_client(my_ip, 5057)

print(client.call("get_info"))
print("Successor 0:", client.call("get_successor", 0))
print("Successor 1:", client.call("get_successor", 1))
print("Predecessor:", client.call("get_predecessor"))