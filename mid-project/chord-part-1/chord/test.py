#!/usr/bin/python3

import msgpackrpc
import time
import subprocess
import traceback

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
port_to_id = {}
id_to_port = {}
find_successor_req = 0
incorrect = 0
t = 2
t = 0.12

def add_id(id, port):
	if id not in ids:
		ids.append(id)
		ids.sort()
		port_to_id[port] = id
		id_to_port[id] = port

def get_id(port):
	client = new_client("127.0.0.1", port)
	return client.call("get_info")[2]

def get_successor_id(port):
	client = new_client("127.0.0.1", port)
	return client.call("get_successor")[2]

def create(port):
	client = new_client("127.0.0.1", port)
	client.call("create")
	add_id(get_id(port), port)
	print("info: node {} with id {} created a chord ring".format(port, get_id(port)))

def join(port1, port2):
	''' port1 join port2 '''
	client1 = new_client("127.0.0.1", port1)
	client2 = new_client("127.0.0.1", port2)
	c2 =  client2.call("get_info")
	client1.call("join",c2)
	port1_id =  get_id(port1)
	add_id(port1_id, port1)
	print("info: node {} with id {} joined node {}".format(port1, port1_id, port2))

# subprocess.run(["make"])
killall_running_nodes()
try:
	
	time.sleep(0.5)
	cmd_str = "./chord 127.0.0.1 5057 & ./chord 127.0.0.1 5058 & ./chord 127.0.0.1 5059 &"
	subprocess.run(cmd_str, shell=True)
	time.sleep(t)
except:
	print("info: start nodes error")

'''
port  id
57    71
58   132
59    37
'''
try:
	# operations
	create(5057)
	join(5059, 5057)
	time.sleep(t)

	join(5058, 5057)
	time.sleep(t)
except Exception as e:
	print(traceback.format_exc())

try:
	# results
	time.sleep(t)
	print('------------')
	for id in ids:
		port = id_to_port[id]
		sid = get_successor_id(port)
		print(f"port {port} | {id}'s successor is {sid}")
except Exception as e:
	print(traceback.format_exc())

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
killall_running_nodes()
print("done")
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
'''
Mine code has error
void stablize(){
  // std::cout << "stablize: enter " << self.id << std::endl;
  if ( !successor.id ){
    return;
  }
  rpc::client *s;
  Node candidate_s;
  // try {
    // get successor.predecessor (沒被插隊的話，會是我自己)
    // std::cout << "stablize: call get_predecessor "  << self.id << std::endl;
    if ( self.id == successor.id ){ // self is the root of ring
      candidate_s = predecessor;
    }
    if ( self.id != successor.id ){
      s = new rpc::client(successor.ip, successor.port); 
      candidate_s = s->call("get_predecessor").as<Node>();
    }
    std::cout << "stablize: "<<self.id<<"'s candidate_s is "<<candidate_s.id<< \
    " current succ is "<<successor.id<< std::endl;

    // check 是否被別人插隊，如果有則插隊的人是我的新 successor
    // if (s <- p <- n), p is my new successor
    if ( candidate_s.id && isBetween(candidate_s.id, self.id, successor.id) ){
      successor = candidate_s;
      delete s;
      // std::cout << "stablize: delete OK" << std::endl;
      s = new rpc::client(successor.ip, successor.port);
    }

    // notify successor that i'm yours predecessor
    s->call("notify", self);
  // } catch (std::exception &e) {
  //   if (!hasError){
  //     std::cout << "chord stablize Err at " << self.id << "\n";
  //     hasError = true;
  //   }
  // }
}
'''

"""
3/28 backup
/**
 * stabilize() 檢查我和繼任者中間是否被插隊，有則換掉我的繼任者為n'，並通知繼任者n'。
 * notify(n') 修正我的前任，此方法由別人喚醒。
 * ex: N21 檢查自己和 N32 之間，被 N24 插入，new 繼任者 is N24。
*/
void stablize(){
  try {

    Node candidate_s;
    rpc::client *client; 

    // i'm the root node of ring and dont have successor
    // if (successor.id == 0 || self.id == successor.id) {
    //   candidate_s = predecessor;
    //   initiate_ring();
    //   // return; // cannot return
    // }

    // Get successor's predecessor
    // case 1: successor's predecessor is myself
    // case 2: successor's predecessor is a new inserted node
    if ( successor.id != 0 && self.id != successor.id ) {

      client = new rpc::client(successor.ip, successor.port); 
      candidate_s = client->call("get_predecessor").as<Node>();

    } else { // when i'm root node [self.id == successor.id]
      candidate_s = predecessor;
      // std::cout << "stablize: Node: "<<self.id<<" has candidate_s: "<< candidate_s.id << "\n";
    }

    if (candidate_s.id != 0) { // case 2
      if ( isBetween(candidate_s.id, self.id, successor.id) ) {
        successor = candidate_s;
      } 
    } 
    
    if ( successor.id != 0 && self.id != successor.id) {
      // if (temp_su_id != successor.id) { // if successor change, tell it to change predecessor

      // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
      // std::cout << "    Out Self id:" << self.id << " Successor id: " << successor.id << "\n";
      // client = new rpc::client(successor.ip, successor.port);
      // client->call("notify", self);
      rpc::client client2(successor.ip, successor.port);
      client2.call("notify", self);

      update_successor_list(successor);
"""