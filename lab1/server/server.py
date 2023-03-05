from flask import Flask

app = Flask(__name__)

@app.route('/')
def get():
    with open('data/msg.txt', 'w') as f:
        f.write("Hi!\n")
    print("server get your request.")
    return "Hi!"

app.run()
