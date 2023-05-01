import msgpackrpc
import subprocess

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))


# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")


client = new_client(my_ip, 5057)
client.call("kill")