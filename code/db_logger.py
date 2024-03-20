import json
from db_connect import SingletonDatabaseConnect
from db_classes import *
import functools


with open('../data/secrets.json', 'r') as f:
    secrets = json.load(f)

username = secrets['username']
password = secrets['password']
database_name = secrets['test_db_name']  
hostname = secrets['hostname']

db_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"

def log_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db_connect = SingletonDatabaseConnect(db_url)
        session = db_connect.get_session()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                log = Log(
                    func=func.__name__,
                    kwargs=str(kwargs)
                )
                session.add(log)
                session.commit()
            except Exception as db_e:
                print(f"Failed to log exception to database: {db_e}")
            finally:
                session.close()
            return str(e)
    return wrapper