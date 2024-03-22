from functools import wraps
from db_classes import Log
from sqlalchemy.exc import SQLAlchemyError
import json

def log_to_db(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        kwargs_str = json.dumps(kwargs)
        session = self.session  # remove the `await` keyword
        if session is None:
            raise ValueError('A session is required')
        try:
            result = await func(self, *args, **kwargs)
            session.add(Log(func=func.__name__, kwargs=kwargs_str, status=f"OK"))
            await session.commit()
            return result
        except Exception as e:
            session.add(Log(func=func.__name__, kwargs=kwargs_str, status="FAIL", message=f"{str(e)}"))
            await session.commit()
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