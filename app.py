import typing
from flask import Flask, request, Response
from utils.hash_utils import encrypt_input, decrypt_input
import os
from models.models import db, Users
from constants import *

app = Flask(__name__)

#Database Configuration
db_user_name:str = os.environ["mysqluser"]
db_passwd:str = os.environ["mysqlpass"]
port:str = os.environ["mysqlport"]
db_name:str = os.environ["dbname"]
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{db_user_name}:{db_passwd}@localhost:{port}/{db_name}".format(db_user_name = db_user_name, db_passwd = db_passwd, port = port, db_name = db_name)

# initialize DB with app variable
db.init_app(app)

@app.route("/")
def hello_world():
    # print(Users.qu ery.all())
    return "NPass Making in Progress !!"


@app.route("/addUser", methods = ['POST'])
def add_new_user():
    '''
    TODO: Validate Email and other params. 
    '''
    try:
        req_body = request.json
        if ("email" not in req_body or "username" not in req_body or "password" not in req_body):
            raise ValueError(MISSING_PARAMS_ERROR)
        
        if len(req_body["password"]) > 16:
            raise ValueError(PASSSWORD_LENGTH_ERROR)
        
        parsed_mail = req_body["email"].split("@")
        id: str = parsed_mail[0] + "-" + parsed_mail[1].split(".")[0]
        message = USER_TEST_MESSAGE
        encrypted_message = encrypt_input(message, req_body["password"])

        exists = db.session.query(Users.email).filter_by(email = req_body["email"]).first() is not None
        if exists:
            raise ValueError(EMAIL_EXISTS_ERROR)
        
        new_user = Users(UserID = id, email = req_body["email"], UserName = req_body["username"], HashedMessage = encrypted_message)
        db.session.add(new_user)
        db.session.commit()

        return USER_CREATION_SUCCESS
    
    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print(e)
        return Response("unable to create User. PLease try again later", status=400)


@app.route("/validateUser", methods = ['POST'])
def validate_user():
    try:
        req_body = request.json
        if ("email" not in req_body or "password" not in req_body):
            raise ValueError(MISSING_PARAMS_ERROR)
        
        user_encrypted_message = db.session.query(Users.HashedMessage).filter_by(email = req_body["email"]).first()
        if user_encrypted_message is None:
            # user not present
            raise Exception()
        
        decrypted_data = decrypt_input(user_encrypted_message[0], req_body["password"])
        if decrypted_data is None or decrypted_data != USER_TEST_MESSAGE:
            # if password is correct, then 
            raise Exception()
        
        return str(True)    
        
    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print("Exception at validate User")
        return Response(INVALID_USER, status=400)
    
