from db_handler import *
from db_connect import SingletonDatabaseConnect
import time

with open('../data/config.json', 'r') as f:
    config = json.load(f)

LOG_LIMIT = config['log_limit'] if 'log_limit' in config else 100
LOG_LIMIT_INTERVAL = config['log_limit_interval'] if 'log_limit_interval' in config else 60

class LogCleanupService:
    def __init__(self, limit=LOG_LIMIT, interval=LOG_LIMIT_INTERVAL):
        self.limit = limit
        self.interval = interval

    def run(self):
        while True:
            session = SingletonDatabaseConnect.connect_from_config().get_session()
            self.limit_log_size(session)
            session.close()
            time.sleep(self.interval)

    def limit_log_size(self, session):
        log_count = session.query(Log).count()
        if log_count > self.limit:
            logs_to_delete = session.query(Log).order_by(Log.id).limit(log_count - self.limit)
            logs_to_delete.delete(synchronize_session=False)
            session.commit()