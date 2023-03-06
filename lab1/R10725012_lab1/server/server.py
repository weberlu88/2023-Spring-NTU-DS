from flask import Flask

import os

app = Flask(__name__)
os.makedirs('data', exist_ok=True)

@app.route('/')
def get():
    with open('data/msg.txt', 'w') as f:
        f.write("Hi!\n")
    print("Get your request. Create data/msg.txt")
    return "Hi!"

app.run()
