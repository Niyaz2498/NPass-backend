from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry
def get_schema_for_user_table(table_name: str, metadata: MetaData) -> Table:
    return Table(table_name, 
                 metadata, 
                 Column('ID', Integer, primary_key=True, autoincrement=True),
                 Column('Site', String(100), nullable=False),
                 Column('Login', String(100)),
                 Column('Password', String(100)),
                 Column('Description', String(500))
                 )