#!/usr/bin/python3

import msgpackrpc
import time
import subprocess

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def killall_running_nodes():
	# Get list of all processes with name starting with "chord"
	try:
		processes = subprocess.check_output(["pgrep", "chord"], universal_newlines=True).split()
		# Kill each process in the list
		for pid in processes:
			subprocess.run(["kill", pid])
			
		print(f"info: Killed {len(processes)} chord processes.")
	except:
		print("info: no runnung chord processes.")

# 助教的 test functions
ids = []
find_successor_req = 0
incorrect = 0
t = 2
t = 0.11

def add_id(id):
	if id not in ids:
		ids.append(id)
		ids.sort()

def get_id(port):
	client = new_client("127.0.0.1", port)
	return client.call("get_info")[2]

def create(port):
	client = new_client("127.0.0.1", port)
	client.call("create")
	add_id(get_id(port))
	print("info: node {} with id {} created a chord ring".format(port, get_id(port)))

def join(port1, port2):
	''' port1 join port2 '''
	client1 = new_client("127.0.0.1", port1)
	client2 = new_client("127.0.0.1", port2)
	client1.call("join", client2.call("get_info"))
	add_id(get_id(port1))
	print("info: node {} joined node {}".format(port1, port2))

# subprocess.run(["make"])
killall_running_nodes()
try:
	
	time.sleep(0.5)
	cmd_str = "./chord 127.0.0.1 5057 & ./chord 127.0.0.1 5058 & ./chord 127.0.0.1 5059 &"
	subprocess.run(cmd_str, shell=True)
	time.sleep(1)
except:
	print("info: start nodes error")

create(5057)
join(5059, 5057)
time.sleep(t)

# join(5060, 5057)
# time.sleep(t)
# client_1 = new_client("127.0.0.1", 5057)
# client_2 = new_client("127.0.0.1", 5058)
# client_3 = new_client("127.0.0.1", 5059)

# print(client_3.call("get_info")) # id  373792412
# print(client_1.call("get_info")) # id  716540891
# print(client_2.call("get_info")) # id 1324994620


# client_1.call("create")
# time.sleep(3)
# client_2.call("join", client_1.call("get_info"))
# time.sleep(3)
# client_3.call("join", client_1.call("get_info"))

# test the functionality after all nodes have joined the Chord ring
# print(client_1.call("find_successor", 123))
# print(client_2.call("find_successor", 123))

# terminate all task
# try:
# 	client_1.call("kill")
# except Exception as e:
# 	print(f'info: kill client_1 error ') # {e}
# try:
# 	client_2.call("kill")
# except Exception as e:
# 	print(f'info: kill client_2 error ') # {e}
# try:
# 	client_3.call("kill")
# except Exception as e:
# 	print(f'info: kill client_3 error ') # {e}
