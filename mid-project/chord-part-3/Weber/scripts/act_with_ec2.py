import msgpackrpc
import sys

'''
get_info / create / join / find_successor / kill
Node get_predecessor()
Node get_successor(int i) i = 0,1,2
'''
def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def check_chord_alive(alais_ip:str) -> bool:
    ''' test if chord service available at 5057 '''
    client = new_client(alais_ip, 5057)
    try:
        info = client.call("get_info")
        if info[0] != b'':
            print("info[0]:", info[0], "type:", type(info[0]))
            return True
    except Exception as e:
        print("chord not-alive at instance:", alais_ip)
    return False

def get_predecessor_and_successor(alais_ip:str):
    ''' get the node's predecessor_and_successor '''
    client = new_client(alais_ip, 5057)
    try:
        node = client.call("get_predecessor")
        pre_ip = node[0].decode()
        print(f"get_predecessor of this node is: {pre_ip}")
    except Exception as e:
        print("get_predecessor failed (warning)")
    try:
        node = client.call("get_successor", 0)
        suc_ip = node[0].decode()
        print(f"get_successor(0) of this node is: {suc_ip}")
    except Exception as e:
        print("get_successor failed (warning)")

def find_successor(alais_ip:str, id:int=1111):
    ''' test if find_successor with key id works '''
    client = new_client(alais_ip, 5057)
    try:
        node = client.call("find_successor", id)
        node_ip = node[0].decode()
        print(f"find_successor id: {id}'s successor is {node_ip}")
    except:
        print(f"find_successor id: {id} failed (warning)")

''' test commands '''
ec2_in_group = '3.92.46.122'
ec2_normal = '54.152.22.41'
localhost = '127.0.0.1'

# filename = sys.argv[1]
ip = sys.argv[1]

# check_chord_alive(ec2_in_group)
# check_chord_alive(ec2_normal)
check_chord_alive(ip)
get_predecessor_and_successor(ip)
find_successor(ip)
print('well done\n')