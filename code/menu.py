import json
from db_connect import SingletonDatabaseConnect
from db_handler import *

with open('../data/secrets.json', 'r') as f:
    secrets = json.load(f)

username = secrets['username']
password = secrets['password']
database_name = secrets['db_name']  
hostname = secrets['hostname']

db_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
db_connect = SingletonDatabaseConnect(db_url)

session = db_connect.get_session()

# import db_classes after the engine is created
from db_classes import *
# delete all tables
Base.metadata.drop_all(db_connect.get_engine())
# create tables
Base.metadata.create_all(db_connect.get_engine())

db_h = DatabaseHandler(session)
user_h = UserHandler(session)
admin_user_h = AdminUserHandler(session)

# create admin user
admin = admin_user_h.create_admin_user(
                    username='admin',
                    password='password',
                    email='admin@email.com',
                    admin_status='full'
                    )

# create user
user = user_h.create_user(
                    username='user',
                    password='password',
                    email='user@email.com'
                    )