import msgpackrpc

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