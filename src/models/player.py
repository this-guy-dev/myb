import sqlite3
import json

from src.models.item import Item

from src.models.base import Base


class Player(Base):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.c.execute('''SELECT user, current_location FROM wars_players WHERE user=?''', (user,))
        user_check = self.c.fetchone()
        if not user_check:
            inventory = []
            inventory_json = json.dumps(inventory)
            self.c.execute('''INSERT OR IGNORE INTO wars_inventory Values (?, ?)''', (self.user, inventory_json))
            self.c.execute('''INSERT OR IGNORE INTO wars_balance Values (?, ?, ?)''', (self.user, 0, 0))
            self.c.execute('''INSERT OR IGNORE INTO wars_players Values (?, ?)''', (self.user, 1))
            self.conn.commit()
            self.current_location = 1
        else:
            self.current_location = user_check[1]

    def get_inventory(self):
        self.c.execute('''SELECT user, inventory FROM wars_inventory WHERE user=?''', (self.user,))
        user, inventory = self.c.fetchone()
        inventory_list = json.loads(inventory)
        return inventory_list

    def get_balance(self):
        self.c.execute('''SELECT wallet, bank FROM wars_balance WHERE user=?''', (self.user,))
        raw_balances = self.c.fetchone()
        balances = {'wallet': raw_balances[0], 'bank': raw_balances[1]}
        return balances

    def add_balance(self, account, amount):
        if account not in ['bank', 'wallet']:
            raise Exception('wallet or bank')
        balance = self.get_balance()
        balance[account] = balance[account] + amount
        self.c.execute('''UPDATE wars_balance SET ''' + account + '''=? WHERE user=?''', (balance[account], self.user))
        self.conn.commit()

    def add_to_inventory(self, item_id, count):
        self.c.execute('''SELECT user, inventory FROM wars_inventory WHERE user=?''', (self.user,))
        user, inventory = self.c.fetchone()
        inventory_list = json.loads(inventory)
        updated_inventory = []
        updated = False
        for inventory_item in inventory_list:
            if inventory_item['id'] == item_id:
                inventory_item['count'] = inventory_item['count'] + count
                updated = True
            updated_inventory.append(inventory_item)
        if updated:
            inventory = json.dumps(updated_inventory)
        else:
            updated_inventory.append({'id': item_id, 'count': count})
            inventory = json.dumps(updated_inventory)
        self.c.execute('''UPDATE wars_inventory SET inventory=? WHERE user=?''', (inventory, self.user))
        self.conn.commit()

    def move_to(self, location_id):
        self.current_location = location_id
        self.c.execute('''UPDATE wars_players SET current_location=? WHERE user=?''', (location_id, self.user))
        self.conn.commit()



