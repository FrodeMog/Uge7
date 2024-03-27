from functools import wraps
from db_classes import Log
from sqlalchemy.exc import SQLAlchemyError
import json

def log_to_db(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        message = kwargs.pop('log_message', None)  # Get the log message if it exists
        kwargs_copy = kwargs.copy()
        if 'password' in kwargs_copy:
            kwargs_copy['password'] = "REMOVED_BY_LOGGER"
        kwargs_str = json.dumps(kwargs_copy)
        
        try:
            result = await func(self, *args, **kwargs)
            self.session.add(Log(func=func.__name__, kwargs=kwargs_str, status=f"OK", message=message))
            await self.session.commit()
            return result
        except Exception as e:
            log_session = await self.db_handler.db_connect.get_new_session()
            log_session.add(Log(func=func.__name__, kwargs=kwargs_str, status="FAIL", message=f"{str(e)}"))
            await log_session.commit()
            raise
    return wrapper

def handle_exceptions_and_rollback(handler):
    @wraps(handler)
    @log_to_db
    async def wrapper(*args, **kwargs):
        try:
            return await handler(*args, **kwargs)
        except SQLAlchemyError:
            await args[0].rollback()  # args[0] is the self argument
            raise
        except Exception as e:
            await args[0].rollback()
            raise ValueError(f"An error occurred: {str(e)}") from e
    return wrapper