import sqlite3
import discord

# noinspection PyPackageRequirements
from discord.ext import commands
from src.models.player import Player
from src.models.item import ItemManager
from src.models.item import Item
from src.models.store import StoreManager
from src.models.location import Location
from src.models.location import LocationManager


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('mybdb.db')
        self.c = self.conn.cursor()
        self.items = ItemManager()
        self.stores = StoreManager()
        self.locations = LocationManager()

        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_inventory (user int, inventory text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_options (user int, options text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_players (user int, current_location int)''')
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS wars_items 
            (id int, name text, emoji text, description text, price_min int, price_max int)'''
        )
        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_stores (id int, name text, location_id int, settings text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_locations (id int, name text, settings text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS wars_balance (user int, wallet int, bank int)''')

    @commands.command(name='profile', aliases=['p', 'stats', 'i'])
    async def _get_profile(self, ctx):
        """See your player profile, balances, current location and inventory."""
        player = Player(ctx.message.author.id)
        inventory_list = player.get_inventory()
        balances = player.get_balance()
        location = Location(player.current_location)
        stores = self.stores.at_location(player.current_location)
        stores_str = ''
        for store in stores:
            if store.location.location_id == player.current_location:
                if store != stores[-1]:
                    stores_str = stores_str + store.name + ', '
                else:
                    stores_str = stores_str + store.name
        embed = discord.Embed(
            title='Profile',
            description='Current Location: ' + location.name,
            colour=discord.Colour.gold()
        )
        if stores_str != '':
            embed.add_field(name='Stores:', value=stores_str, inline=False)
        inventory_str = ''
        if len(inventory_list) > 0:
            for inventory in inventory_list:
                item_object = Item(inventory['id'])
                inventory_str = inventory_str + item_object.emoji + '(' + str(inventory['count']) + ') ' + ' ' + item_object.name + '\n'
        else:
            inventory_str = 'Empty Inventory'
        embed.add_field(name='Bank Balance:', value=':moneybag:'+'{:20,.0f}'.format(balances['bank']))
        embed.add_field(name='Cash Balance:', value=':moneybag:'+'{:20,.0f}'.format(balances['wallet']))
        embed.add_field(name='Inventory', value=inventory_str, inline=False)
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Main(bot))
