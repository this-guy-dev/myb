import json
import random

from time import time

from src.models.base import Base


class Utils(Base):
    def __init__(self):
        super().__init__()

    def update_prices(self, item_id=None):
        if item_id:
            self.c.execute('''SELECT id, name, emoji, description, price_min, price_max FROM wars_items WHERE id=?''', (item_id,))
        else:
            self.c.execute('''SELECT id, name, emoji, description, price_min, price_max FROM wars_items''')
        start_time = time()
        raw_items = self.c.fetchall()
        items_list = []
        for raw_item in raw_items:
            item_object = {
                'id': raw_item[0],
                'price_min': raw_item[4],
                'price_max': raw_item[5]
            }
            items_list.append(item_object)
        self.c.execute('''SELECT id, name, location_id, settings FROM wars_stores''')
        raw_stores = self.c.fetchall()
        for raw_store in raw_stores:
            store_id, name, location_id, settings = raw_store
            settings = json.loads(settings)
            if 'prices' in settings.keys():
                prices = settings['prices']
            else:
                prices = dict()
            for item in items_list:
                if item['id'] == item_id or item_id is None:
                    if item['price_min'] >= item['price_max']:
                        prices[item['id']] = item['price_min']
                    else:
                        prices[item['id']] = random.randrange(item['price_min'], item['price_max'])
            prices['date'] = start_time
            settings['prices'] = prices
            settings_json = json.dumps(settings)
            self.c.execute('''UPDATE wars_stores SET settings=? WHERE id=?''', (settings_json, store_id))
            self.conn.commit()
        return
