from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import asynccontextmanager
import json
import asyncio
import os

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
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the file
        file_path_secrets = os.path.join(script_dir, '..', 'data', 'secrets.json')
        file_path_config = os.path.join(script_dir, '..', 'data', 'config_async.json')

        with open(file_path_secrets, 'r') as f:
            secrets = json.load(f)

        with open(file_path_config, 'r') as f:
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

class AsyncDatabaseConnect:
    def __init__(self, db_url):
        self.engine = create_async_engine(
            db_url,
            connect_args={'connect_timeout': 5}
            #,echo=True
        )
        self.sessionmaker = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def get_new_session(self):
        self.session = self.sessionmaker()
        return self.session

    async def close(self):
        await self.session.close()
        await self.engine.dispose()
            
    @staticmethod
    async def connect_from_config():
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the file
        file_path_secrets = os.path.join(script_dir, '..', 'data', 'secrets.json')
        file_path_config = os.path.join(script_dir, '..', 'data', 'config_async.json')

        with open(file_path_secrets, 'r') as f:
            secrets = json.load(f)

        with open(file_path_config, 'r') as f:
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
        db_connect = AsyncDatabaseConnect(db_url)

        return db_connect