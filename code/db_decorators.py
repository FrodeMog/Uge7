from sqlalchemy.orm import Session
from db_connect import SingletonDatabaseConnect
from functools import wraps
from db_classes import Log
from sqlalchemy.exc import SQLAlchemyError
import json

session = SingletonDatabaseConnect.connect_from_config().get_session()

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

def handle_exceptions_and_rollback(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except SQLAlchemyError:
            args[0].rollback()  # args[0] is the self argument
            raise
        except Exception as e:
            args[0].rollback()
            raise ValueError(f"An error occurred: {str(e)}")
    return wrapper