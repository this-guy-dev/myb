import sqlite3
import json

from src.models.item import Item
from src.models.item import ItemManager
from src.models.location import Location
from src.models.base import Base
from time import time


class Store(Base):
    def __init__(self, store_id):
        super().__init__()
        self.c.execute('''SELECT id, name, location_id, settings FROM wars_stores WHERE id=?''', (store_id,))
        fetch = self.c.fetchone()
        if not fetch:
            raise Exception('No store with that id')
        store_id, name, location_id, settings = fetch
        self.store_id = store_id
        self.name = name
        self.location = Location(location_id)
        self.settings = json.loads(settings)
        if self.settings['available_items']:
            self.available_items = self.settings['available_items']
        else:
            self.available_items = ItemManager().list_id()

        if 'thumbnail' in self.settings.keys():
            self.thumbnail = self.settings['thumbnail']

    def set_thumbnail(self, url):
        self.settings['thumbnail'] = url
        settings_json = json.dumps(self.settings)
        self.c.execute('''UPDATE wars_stores SET settings=? WHERE id=?''', (settings_json, self.store_id))
        self.conn.commit()


class StoreManager(Base):
    def __init__(self):
        super().__init__()
        self.items = ItemManager()

    def list(self):
        self.c.execute('''SELECT id, name, location_id, settings FROM wars_stores''')
        raw_stores = self.c.fetchall()
        stores = []
        for store in raw_stores:
            stores.append({'id': store[0], 'name': store[1], 'location_id': store[2], 'settings': store[3]})
        return stores

    def list_id(self):
        self.c.execute('''SELECT id FROM wars_stores''')
        raw_stores = self.c.fetchall()
        return [x[0] for x in raw_stores]

    def at_location(self, location_id):
        stores = []
        store_ids = self.list_id()
        for store_id in store_ids:
            store = Store(store_id)
            if store.location.location_id == location_id:
                stores.append(store)
        return stores

    def add(self, name, location_id, set_id=None, items=None):
        if items is None:
            items = []
        self.c.execute('''SELECT id, name, location_id FROM wars_stores WHERE name=?''', (name,))
        fetch = self.c.fetchone()
        if fetch:
            raise Exception('existing name')
        else:
            self.c.execute('''SELECT MAX(id) FROM wars_stores''')
            fetch = self.c.fetchone()
            max_id = fetch[0]
            if max_id is None:
                max_id = 0
            if set_id is None:
                set_id = max_id + 1
            settings = dict()
            prices = dict()
            for item in self.items.list():
                prices[item['id']] = Item(item['id']).get_price()
            prices['date'] = time()
            settings['prices'] = prices
            settings['available_items'] = items
            settings_json = json.dumps(settings)
            self.c.execute('''INSERT INTO wars_stores Values (?, ?, ?, ?)''', (set_id, name, location_id, settings_json))
            self.conn.commit()
            return
