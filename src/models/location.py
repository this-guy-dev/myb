import sqlite3
import json

from src.models.base import Base


class Location(Base):
    def __init__(self, store_id):
        super().__init__()
        self.c.execute('''SELECT id, name, settings FROM wars_locations WHERE id=?''', (store_id,))
        fetch = self.c.fetchone()
        if not fetch:
            raise Exception('No location with that id')
        location_id, name, settings = fetch
        self.location_id = location_id
        self.name = name
        self.settings = json.loads(settings)


class LocationManager(Base):

    def list(self):
        self.c.execute('''SELECT id, name FROM wars_locations''')
        raw_locations = self.c.fetchall()
        locations = []
        for location in raw_locations:
            locations.append({'id': location[0], 'name': location[1]})
        return locations

    def add(self, name, set_id=None):
        self.c.execute('''SELECT id, name FROM wars_locations WHERE name=?''', (name,))
        fetch = self.c.fetchone()
        if fetch:
            raise Exception('existing name')
        else:
            self.c.execute('''SELECT MAX(id) FROM wars_locations''')
            fetch = self.c.fetchone()
            max_id = fetch[0]
            if max_id is None:
                max_id = 0
            if set_id is None:
                set_id = max_id + 1
            settings = dict()
            settings_json = json.dumps(settings)
            self.c.execute('''INSERT INTO wars_locations Values (?, ?, ?)''', (set_id, name, settings_json))
            self.conn.commit()
            return
