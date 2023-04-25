import time
import subprocess
import boto3
import msgpackrpc

'''
Get current machine's private_ip, and get other running ec2 instances' private_ip.
If other instance found, select a chord node to Join.
Else start the chord ring by myself.
'''
def new_client(ip, port):
	return msgpackrpc.Client(msgpackrpc.Address(ip, port))

def check_chord_alive(alais_ip:str) -> bool:
    ''' test if chord service available at 5057 '''
    client = new_client(alais_ip, 5057)
    try:
        info = client.call("get_info")
        if info[0] != b'':
            print("check_chord_alive:", info[0], "type:", type(info[0]))
            return True
    except Exception as e:
        print("chord not-alive at instance:", alais_ip)
    return False

def join_chord(my_ip, chord_ip):
    ''' my_ip will join chord_ip '''
    client_1 = new_client(chord_ip, 5057) # who help to join
    client_2 = new_client(my_ip, 5057) # the new node on local machine

    c1_info = client_1.call("get_info")
    client_2.call("join", c1_info)
    # print("info: node {} with id {} joined node {}".format(port1, port1_id, port2))

def create_chord_ring(my_ip):
    client = new_client(my_ip, 5057)
    client.call("create")
    time.sleep(2)

def restart_chord_node(private_ip):
	# Get list of all processes with name starting with "chord" and kill
	try:
		processes = subprocess.check_output(["pgrep", "chord"], universal_newlines=True).split()
		# Kill each process in the list
		for pid in processes:
			subprocess.run(["kill", pid])
			
		print(f"info: Killed {len(processes)} chord processes.")
	except:
		print("info: no runnung chord processes.")
	try:
		cmd_str = f"/home/ec2-user/chord {private_ip} 5057 &"
		subprocess.run(cmd_str, shell=True)
		time.sleep(2.1)
	except:
		print("info: start nodes error")

''' (1) Get current machine's private_ip, and get other running ec2 instances' private_ip. ''' 

alias_ip_list = []
private_ip = subprocess.check_output(["hostname", "-i"], universal_newlines=True).strip() #.split()
print("my private_ip:", private_ip)
# same as hostname -i
# private_ip = subprocess.check_output(["curl", "-s", "http://169.254.169.254/latest/meta-data/local-ipv4"]).decode('utf-8')

ec2 = boto3.client('ec2', region_name='us-east-1')
response = ec2.describe_instances()
# response = ec2.describe_regions()
# print(response)

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        if 'PrivateIpAddress' in instance: # if the EC2 is terminated, it will not have the private ip
            # print("instance:", instance, "\n")
            if instance['PrivateIpAddress'] != private_ip:
                alias_ip_list.append(instance['PrivateIpAddress'])
print("alias_ip_list:", alias_ip_list)

''' (2) If other instance found, select a chord node to Join. Else start the chord ring by myself.'''
restart_chord_node(private_ip)
isJoinSucc = False

for alias_ip in alias_ip_list:
    if check_chord_alive(alias_ip):
        print("Try join a chord ring at:", alias_ip)
        join_chord(private_ip, alias_ip)
        isJoinSucc = True
        print("Join a chord ring at:", alias_ip)
        break

if not isJoinSucc:
    print("No alias found, try to create chord ring")
    create_chord_ring(private_ip)
    print("Create a new chord ring at:", private_ip)
print()
