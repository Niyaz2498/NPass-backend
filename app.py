import os
from constants import *
from flask import Flask, request, Response
from sqlalchemy import  MetaData, Table
from sqlalchemy.orm import registry
from utils.general_utils import get_table_name_from_email
from utils.hash_utils import encrypt_input, decrypt_input
from models.models import db, Users
from utils.sql_utils import check_for_user_auth, create_custom_model_imperative, get_schema_for_user_table

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
        
        id: str = get_table_name_from_email(req_body["email"])
        message = USER_TEST_MESSAGE
        encrypted_message = encrypt_input(message, req_body["password"])

        exists = db.session.query(Users.email).filter_by(email = req_body["email"]).first() is not None
        if exists:
            raise ValueError(EMAIL_EXISTS_ERROR)
        
        new_user = Users(UserID = id, email = req_body["email"], UserName = req_body["username"], HashedMessage = encrypted_message)
        db.session.add(new_user)
        secret_table_status = create_user_secrets_table(id)
        print(secret_table_status)
        if not secret_table_status:
            print( "Problem creating user Table")
            raise Exception()
        db.session.commit()

        return USER_CREATION_SUCCESS
    
    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print(e)
        return Response("unable to create new user. Please try again later", status=400)

def create_user_secrets_table(table_name: str) -> bool:

    '''
        Imperative way to create a table. 
        Following this since the table name is dynamic 
        Ideally we have a table for each users.
    '''

    try:
        engine = db.get_engine()
        metadata = MetaData()
        user_table: Table = get_schema_for_user_table(table_name, metadata)
        metadata.create_all(engine)
        return True
    except Exception as e:
        print("unable to create User secrets table ")
        print(e)
        return False


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
    

@app.route("/querySecrets", methods = ['POST'])
def query_secret():
    '''
    TODO: decrypt with master password before returning  
    '''
    try:
        req_body = request.json
        
        if "email" not in req_body:
            raise ValueError(EMAIL_MISSING_ERROR)
        
        table_name = get_table_name_from_email(req_body["email"])
        custom_model = create_custom_model_imperative(db, table_name)
        
        resp_obj = []
        for i in db.session.query(custom_model).all():
            row_obj = {}
            row_obj['Site'] = i.Site
            row_obj['Login'] = i.Login
            row_obj['Password'] = i.Password
            row_obj['Description'] = i.Description
            resp_obj.append(row_obj)

        return str({
            "secrets": resp_obj
        })


    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print("Exception in querying User secrets")
        print(e)
        return Response(INVALID_USER, status=400) 


@app.route("/addNewSecret", methods = ['POST'])
def add_new_secret():
    '''
    TODO: encrypt before adding 
    '''
    try:
        req_body = request.json
        master_password = req_body.get('MasterPassword', '')
        email = req_body.get('Email', '')
        site = req_body.get('Site', '')
        login = req_body.get('Login', '')
        password = req_body.get('Password', '')
        description = req_body.get('Description', '')

        if master_password == '' or email == '' or site == '':
            raise ValueError("missing params")
        
        if check_for_user_auth(db, master_password, email) == False:
            raise Exception()
        
        table_name = get_table_name_from_email(email)
        custom_model = create_custom_model_imperative(db, table_name)
        new_secrets = custom_model(Site= site, Login = login, Password = password, Description = description)
        db.session.add(new_secrets)
        db.session.commit()

        return str(True)

    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print("Exception in querying User secrets")
        print(e)
        return Response(INVALID_USER, status=400) 
    

@app.route("/updateSecret", methods = ['POST'])
def update_secret():
    '''
    TODO: encrypt before Update 
    '''
    try:
        req_body = request.json
        master_password = req_body.get('MasterPassword', '')
        email = req_body.get('Email', '')
        field = req_body.get('Field', '')
        value = req_body.get('Value', '')
        id = int(req_body.get('ID', ''))

        if master_password == '' or email == '' or field == '' or value == '' or id == '':
            raise ValueError("missing params")
        
        if check_for_user_auth(db, master_password, email) == False:
            raise Exception()
        
        table_name = get_table_name_from_email(email)
        custom_model = create_custom_model_imperative(db, table_name)
        secret_obj = db.session.query(custom_model).filter_by(ID = id).first()

        match field:
            case "Site":
                print("site: ", secret_obj.Site)
                secret_obj.Site = value
            case "Login":
                print("Login: ", secret_obj.Login)
                secret_obj.Login = value
            case "Password":
                print("Password: ", secret_obj.Password)
                secret_obj.Password = value
            case "Description":
                print("Description: ", secret_obj.Description)
                secret_obj.Description = value
            case default:
                raise ValueError("Invalid field")
            
        db.session.commit()

        return str(True)
    
    except ValueError as v:
        return Response(str(v), status=400)
    except Exception as e:
        print("Exception in update secrets")
        print(e)
        return Response(INVALID_USER, status=400)  