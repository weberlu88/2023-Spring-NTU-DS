#!/bin/bash
sudo yum install -y python3-pip python3 python3-setuptools -y
/usr/bin/python3 -m pip install boto3 ec2_metadata uploadserver msgpack-rpc-python

# aws configure
aws configure set aws_access_key_id ASIA5MU4OC5PBMFKEHCV
aws configure set aws_secret_access_key uaWqalQ74DF25x6bQPES+cCbHpvWEJE2xrduCjOY
aws configure set aws_session_token FwoGZXIvYXdzEB0aDI8a8H3tgi0Akda0+CLKAVQFQz+zxckKmDOidAZq3Yi/43UW+8etqcB/oYpNKihwGt3wbc8pUw8rTxGWqK6bxDfoJBo6qmbNqx/yd9uZYjTSP9mfkXqW8Gj92WmhfQ1qnhihQFAa8AA6LIuqKOv/oVQv4Mmjw1St5FP6BrcHgkswlRqaGEIPewZDK/AUoeoQ0ruWz1n+RA1irUL892v/z/eSIABnwXAqp7rAs4Fd677Kynf8CyBMwZlcelVfUORRNvt3FLxS1poXAcVhaAoe8/HOlfA9WnChroEo5/CeogYyLbO2w8oVnzA2GMO5vHmJKwl7MWuzvJnqlcg7UmpfrPCoYZfFkNkAiu53vsn77g==

# run service
/usr/bin/python3 /home/ec2-user/init_script.py
/usr/bin/python3 -m uploadserver 5058 --directory /home/ec2-user/files
