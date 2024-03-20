from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class SingletonDatabaseConnect:
    instance = None
    session = None

    def __new__(cls, db_url):
        if cls.instance is None:
            cls.instance = super(SingletonDatabaseConnect, cls).__new__(cls)
            cls.instance.engine = create_engine(
                db_url,
                connect_args={'connect_timeout': 5}
            )
            cls.session = scoped_session(sessionmaker(bind=cls.instance.engine))
        return cls.instance

    def get_session(self):
        return self.session
    
    def get_engine(self):
        return self.engine