from flask import Flask
from utils.hash_utils import hash_fun

app = Flask(__name__)

@app.route("/")
def hello_world():
    print(hash_fun())
    return "This is a Simple flask app. Making Password manager backend is in progress"