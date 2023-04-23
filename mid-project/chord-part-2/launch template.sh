#!/bin/bash
sudo yum install -y python3-pip python3 python3-setuptools -y
/usr/bin/python3 -m pip install boto3 ec2_metadata uploadserver msgpack-rpc-python

# aws configure
aws configure set aws_access_key_id ASIA5MU4OC5PM3PQVAOO
aws configure set aws_secret_access_key rBaCbzopfdP1A4vReV8DqEyncqSiItkpIl0u9fVt
aws configure set aws_session_token FwoGZXIvYXdzENL//////////wEaDBwlzYPV5eK0+PRsJyLKAdvncTvGmulGbpLFtCn+Oy4EIgAR2U3o1Kwq0SlkFKmkpMNarlbibjmQasKHTTqBfF6saUUmg5Xvn3Vp5Q7biGKHPM7gZ9E/j211ayYNz0CKmMwuTjs0YqrlbGrsHdAuSjXYfrXIx+7h39nPEcXNknos39JULuD8QiJf0parnt0YDRpVzbwwiUkPx41IkqoHAUPSjXjW9IuNT0TgX4URVoOFXmzHrgkJRnRIAGdJWP8PWp9/f5beDzCz4o8UmQrOBw8eeItkhb03F+MoxLaOogYyLXyzuZ5G2+FBI7pFk9mIP03YGDEkAkczgEar7EGHX9cJtXJEWy8HEDLLRowq+w==

# run service
/usr/bin/python3 -m uploadserver 5058 --directory /home/ec2-user/files
/usr/bin/python3 /home/ec2-user/init_script.py