from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import json

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

    @classmethod
    def connect_from_config(cls):

        with open('../data/secrets.json', 'r') as f:
            secrets = json.load(f)

        with open('../data/config.json', 'r') as f:
            config = json.load(f)

        adapter = config['adapter'] 
        test_mode = config['test_mode'].lower() == "true"
        username = secrets['username']
        password = secrets['password']
        hostname = secrets['hostname']

        if test_mode and 'test_db_name' in secrets:
            database_name = secrets['test_db_name']
        else:
            database_name = secrets['db_name']

        db_url = f"{adapter}://{username}:{password}@{hostname}/{database_name}"
        db_connect = cls(db_url)

        return db_connect
