#!/bin/bash
sudo yum install -y python3-pip python3 python3-setuptools -y
/usr/bin/python3 -m pip install boto3 ec2_metadata uploadserver msgpack-rpc-python flask

# aws configure
aws configure set aws_access_key_id ASIA5MU4OC5PGBCO23HN
aws configure set aws_secret_access_key yUal2/DAHQJwjOV41yICnxAQAc1nsEcOo6ph+4Pf
aws configure set aws_session_token FwoGZXIvYXdzEI3//////////wEaDKbqj71RnSPjHvTpZyLKAaVMRm3eElHjUFEwCbf2GcrRecrC0pTQohAs24mzHohPUJOaXEJSrrj9H6QacWR05wSgR1/t6QiPo1sSqZcddwv8D0ynxk3ST31+sslk6wiYvplO1CFnwztA4gongHebCp4UEvBCsybLUQtMjWGwfAjbk4oHuWdiK7MY9A8u7PDhElRrkbtBubEb7lvfexCtGFikmNPyQ5NReMpESbI88E1671CbRara125MJoPW7eD0t6bm63UJb7fLPNNqtnVRFGBwYfoYz1V4R50ol8C3ogYyLWeEYaPKpdXLHAmdYjcwAS4B41aFCh/2mihOTGiM++FXdZsgFUsWy8ma3vtGHw==

# run service
sudo nohup /usr/bin/python3 /home/ec2-user/do_localfile_checkserver.py > flasklog.txt 2>&1 &
/usr/bin/python3 /home/ec2-user/init_script.py
/usr/bin/python3 -m uploadserver 5058 --directory /home/ec2-user/files
