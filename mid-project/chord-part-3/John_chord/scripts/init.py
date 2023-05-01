import boto3
import msgpackrpc
import time
import subprocess

def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def create_ring(my_ip):
    client = new_client(my_ip, 5057)
    client.call("create")
    time.sleep(2)

def join_node(my_ip, target_ip):
    # print("join node...")
    client_1 = new_client(target_ip, 5057) # who help to join
    client_2 = new_client(my_ip, 5057) # the new node

    c1_info = client_1.call("get_info")
    client_2.call("join", c1_info)

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

def get_ec2_ips(is_including_self=True): # including self ip?
    ec2_ip = []
    ec2 = boto3.client('ec2', region_name='ap-southeast-2')
    response = ec2.describe_instances()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if 'PublicIpAddress' in instance: 
            # if 'PrivateIpAddress' in instance: 
                # print("instance:", instance, "\n\n")
                if is_including_self:
                    # ec2_ip.append(instance['PrivateIpAddress'])
                    ec2_ip.append(instance['PublicIpAddress'])
                else:
                    # if instance['PrivateIpAddress'] != my_ip:
                    #     ec2_ip.append(instance['PrivateIpAddress'])
                    if instance['PublicIpAddress'] != my_ip:
                        ec2_ip.append(instance['PublicIpAddress'])

    return ec2_ip

def get_node_ips():  
    ec2_ips = get_ec2_ips(is_including_self=True) 
    node_ips = []
    for ip in ec2_ips:
        if(is_alive_node(ip)):
            node_ips.append(ip)

    return node_ips

### initial chord ###
# my_ip = os.environ.get('CHORD_IP')
# my_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')
my_ip = subprocess.check_output(["curl", "-s", "http://checkip.amazonaws.com"]).decode('utf-8').strip("\n")
print("my_ip:", my_ip)
process = subprocess.Popen(["/home/ec2-user/chord", my_ip, "5057", "&"])
print("activate chord node......")
process.poll()
time.sleep(5)

ec2_ip = get_ec2_ips(is_including_self=True)

# print("my ip:", my_ip)
print("ec2_ip:", ec2_ip)


isJoin = False
for ip in ec2_ip:
    if ip != my_ip:
        if(is_alive_node(ip)):
            print("Alive:", ip)
            print("join", ip)
            join_node(my_ip, ip)
            isJoin = True
            break
        else:
            print("non-Alive:", ip)

if not isJoin:
    print("create!")
    create_ring(my_ip)

