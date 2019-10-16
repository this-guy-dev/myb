import sqlite3
import random

from src.models.base import Base
from src.utils import Utils


class Item(Base):
    def __init__(self, item):
        super().__init__()
        self.c.execute(
            '''SELECT id, name, emoji, description, price_min, price_max FROM wars_items WHERE id=?''',
            (item,)
        )
        item_check = self.c.fetchone()
        if not item_check:
            raise Exception("no item by that id")
        self.id, self.name, self.emoji, self.description, self.price_min, self.price_max = item_check
        self.utils = Utils()

    def edit(self, field, value):
        self.c.execute('''UPDATE wars_items SET ''' + field + '''=? WHERE id=?''', (value, self.id))
        self.conn.commit()
        self.utils.update_prices(self.id)
        self.__init__(self.id)

    def get_price(self):
        try:
            return random.randrange(self.price_min, self.price_max)
        except ValueError:
            return self.price_min


class ItemManager(Base):
    def __init__(self):
        super().__init__()
        self.utils = Utils()

    def list(self):
        self.c.execute('''SELECT id, name, emoji, description, price_min, price_max  FROM wars_items''')

        fetch_all = self.c.fetchall()

        items_list = []

        for fetch in fetch_all:

            item_object = {
                'id': fetch[0],
                'name': fetch[1],
                'emoji': fetch[2],
                'description': fetch[3],
                'price_min': fetch[4],
                'price_max': fetch[5]
            }

            items_list.append(item_object)

        return items_list

    def list_id(self):
        self.c.execute('''SELECT id FROM wars_items''')
        fetch_all = self.c.fetchall()
        return [x[0] for x in fetch_all]

    def new(self, name, emoji, set_id=None, price_min=0, price_max=0, description=''):
        self.c.execute('''SELECT name, emoji FROM wars_items WHERE name=?''', (name,))

        fetch = self.c.fetchone()
        if fetch:
            raise Exception('existing name')
        else:
            self.c.execute('''SELECT MAX(id) FROM wars_items''')
            fetch = self.c.fetchone()
            max_id = fetch[0]
            if max_id is None:
                max_id = 0
            if set_id is None:
                set_id = max_id + 1
            self.c.execute('''INSERT INTO wars_items Values (?, ?, ?, ?, ?, ?)''', (set_id, name, emoji, description,
                                                                                    price_min, price_max))
            self.conn.commit()
            self.utils.update_prices(set_id)
            return

    def remove(self, item_id):
        self.c.execute('''DELETE FROM wars_items WHERE id=?''', (item_id,))
        self.conn.commit()
        return


