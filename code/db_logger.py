from functools import wraps
from db_classes import Log

def log_commit_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = args[0]  # The session is the first argument of the method
        try:
            return func(*args, **kwargs)
        except Exception as e:
            session.rollback()  # Roll back the session to a clean state
            log = Log(
                func=func.__name__,
                kwargs=str(e)  # Store the exception message in kwargs
            )
            session.add(log)
            session.commit()
            raise
    return wrapper