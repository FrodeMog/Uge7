from sqlalchemy.orm import Session
from db_connect import SingletonDatabaseConnect
from functools import wraps
from db_classes import Log
import json

with open('../data/secrets.json', 'r') as f:
    secrets = json.load(f)

username = secrets['username']
password = secrets['password']
database_name = secrets['test_db_name']
hostname = secrets['hostname']

db_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
db_connect = SingletonDatabaseConnect(db_url)

session = db_connect.get_session()


def log_to_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs_str = json.dumps(kwargs)
        try:
            result = func(*args, **kwargs)
            session.add(Log(func=func.__name__, kwargs=kwargs_str, status=f"OK"))
            session.commit()
            return result
        except Exception as e:
            session.add(Log(func=func.__name__, kwargs=kwargs_str, status="FAIL", message=f"{str(e)}"))
            session.commit()
            raise
    return wrapper