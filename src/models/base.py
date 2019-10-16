import sqlite3


class Base:
    def __init__(self):
        self.conn = sqlite3.connect('mybdb.db')
        self.c = self.conn.cursor()
