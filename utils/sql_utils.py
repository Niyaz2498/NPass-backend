from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry
from flask_sqlalchemy import SQLAlchemy
from models.models import Users
from utils.hash_utils import decrypt_input
from constants import USER_TEST_MESSAGE


def get_schema_for_user_table(table_name: str, metadata: MetaData) -> Table:
    return Table(table_name, 
                 metadata, 
                 Column('ID', Integer, primary_key=True, autoincrement=True),
                 Column('Site', String(100), nullable=False),
                 Column('Login', String(100)),
                 Column('Password', String(100)),
                 Column('Description', String(500))
                 )


def check_for_user_auth(db: SQLAlchemy, master_password: str, email: str) -> bool:
    user_encrypted_message = db.session.query(Users.HashedMessage).filter_by(email = email).first()
    if user_encrypted_message is None:
        # user not present
        return False
    
    decrypted_data = decrypt_input(user_encrypted_message[0], master_password)
    if decrypted_data is None or decrypted_data != USER_TEST_MESSAGE:
        # if password is correct, then 
        return False
    
    return True
        
def create_custom_model_imperative(db: SQLAlchemy, table_name: str):
    mapper_registry = registry()
    engine = db.get_engine()
    metadata = MetaData()
    user_table: Table = get_schema_for_user_table(table_name, metadata)
    metadata.create_all(engine)

    class custom_model:
        pass

    mapper_registry.map_imperatively(custom_model, user_table)

    return custom_model