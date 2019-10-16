import contextlib
import sqlite3
import pandas as pd
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'ERROR',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'sqlite.log',
            'mode': 'w',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'sqlite': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    },
}

logging.config.dictConfig(LOGGING)

logger = logging.getLogger('sqlite')


# noinspection PyPep8Naming
class sqlite(object):
    def __init__(self, db_file):
        self.db_file = db_file

    def query(self, query):
        logger.info('Query issued: ' + query)
        try:
            with contextlib.closing(sqlite3.connect(self.db_file)) as conn:  # auto-closes
                with conn:  # auto-commits
                    with contextlib.closing(conn.cursor()) as cursor:   # auto-closes
                        cursor.execute(query)
                        return cursor.fetchall()
        except sqlite3.OperationalError as e:
            logger.error(e)

    def get_table(self, table):
        query = "SELECT * FROM %s" % table
        return self.query_frame(query)

    def add_column(self, table, column, kind):
        query = 'ALTER TABLE %s ADD COLUMN %s %s' % (table, column, kind)
        return self.query(query)

    def table_info(self, table):
        query = "PRAGMA table_info('%s')" % table
        return self.query(query)

    def load_frame(self, frame, table, action='append'):
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:  # auto-closes
            with conn:  # auto-commits
                frame.to_sql(table, conn, index=False, if_exists=action)

    def query_frame(self, query):
        with contextlib.closing(sqlite3.connect(self.db_file)) as conn:  # auto-closes
            with conn:  # auto-commits
                return pd.read_sql(query, conn)

    def rename_table(self, old_table, new_table):
        query = 'ALTER TABLE %s RENAME TO %s' % (old_table, new_table)
        _ = self.query(query)
