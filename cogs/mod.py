import discord
import sqlite3
import json
from time import time
# noinspection PyPackageRequirements
from discord.ext import commands
from src.models.item import ItemManager
from src.models.store import StoreManager
from src.models.store import Store
from src.models.location import LocationManager
from src.models.item import Item
from src.utils import Utils


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('mybdb.db')
        self.c = self.conn.cursor()
        self.items = ItemManager()
        self.stores = StoreManager()
        self.locations = LocationManager()
        self.utils = Utils()

    @commands.command(name='kick', hidden=True)
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        await ctx.trigger_typing()
        await ctx.channel.purge(limit=1)
        if not member:
            return await ctx.send('Missing Member Kick Message')
        await member.kick(reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} kicked by {ctx.author.display_name}",
            description=f"Reason: **{reason}**"
        )
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='ban', hidden=True)
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx,  member: discord.Member = None, *, reason: str = None):
        await ctx.trigger_typing()
        await ctx.channel.purge(limit=1)
        if not member:
            return await ctx.send('Missing Member Kick Message')
        await member.ban(reason=reason)
        embed = discord.Embed(
            title=f"{member.display_name} banned by {ctx.author.display_name}",
            description=f"Reason: **{reason}**"
        )
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)
        return

    @commands.command(name='purge', hidden=True)
    @commands.has_permissions(manage_messages=True)
    async def _purge(self, ctx, count: int = 0):
        await ctx.trigger_typing()
        await ctx.send('The PURGE HAS BEGUN!')
        # time.sleep(2)
        return await ctx.channel.purge(limit=count)

    # Admin Group

    @commands.group(name='admin', invoke_without_command=True, hidden=True)
    async def _admin(self, ctx):
        await ctx.send('try `admin item`')

    @_admin.command(name='updateprices', hidden=True)
    async def _update_prices(self, ctx):
        self.utils.update_prices()
        return await ctx.send('Prices updated.')

    @_admin.command(name='dash')
    async def _dashboard(self, ctx):
        embed = discord.Embed(title='Dashboard', description='Description')
        items = self.items.list()
        items_str = ''
        for item in items:
            items_str = items_str + str(item['id']) + item['emoji'] + item['description'] + '\n'
        embed.add_field(name='Items', value=items_str)
        return await ctx.send(embed=embed)
    # Admin - Item Group

    @_admin.group(name='item', invoke_without_command=True)
    async def _item(self, ctx):
        await ctx.send('try `available options: add, list, delete')

    @_item.command(name='list')
    async def _list_items(self, ctx):
        await ctx.trigger_typing()
        items = self.items.list()
        embed = discord.Embed(title='Available Items', description='Some text')
        for item in items:
            item_object = Item(item['id'])
            if item['price_min'] != item['price_max']:
                market_price = item_object.get_price()
            else:
                market_price = item['price_min']
            embed.add_field(
                name=item['name'],
                value='ID: ' + str(item['id']) +
                      '\nEmoji: ' + item['emoji'] +
                      '\nDescription :' + item['description'] +
                      '\nMin Price: ' + str(item['price_min']) +
                      '\nMax Price: ' + str(item['price_max']) +
                      '\nMarket Price: ' + str(market_price)
            )
        await ctx.send(embed=embed)

    @_item.command(name='delete')
    async def _delete_item(self, ctx, item_id: int = 0):
        self.items.remove(item_id)
        await ctx.send('ID ' + str(item_id) + ' removed.')

    @_item.command(name='add')
    async def _add_item(self, ctx, emoji: str = None, name: str = None):
        if emoji is not None:
            self.items.new(name, emoji)
            await ctx.send("{0} {1} has been added.".format(emoji, name))

    @_item.group(name='set', invoke_without_command=True)
    async def _set_item(self, ctx):
        await ctx.send('available options: price_min, price_max, description, emoji')

    # Admin - Item - Set Group

    @_set_item.command(name='price_min')
    async def _set_item_price_min(self, ctx, item_id: int = 0, price_min: int = 0):
        print(item_id)
        item_object = Item(item_id)
        item_object.edit('price_min', price_min)
        await ctx.send('Min Price Updated. ' + str(item_object.price_min))

    @_set_item.command(name='price_max')
    async def _set_item_price_max(self, ctx, item_id: int = 0, price_max: int = 0):
        item_object = Item(item_id)
        item_object.edit('price_max', price_max)
        await ctx.send('Max Price Updated. ' + str(item_object.price_max))

    @_set_item.command(name='description', aliases=['desc'])
    async def _set_item_description(self, ctx, item_id: int = 0, *, description: str = ''):
        item_object = Item(item_id)
        item_object.edit('description', description)
        await ctx.send('Description Updated. ' + str(item_object.description))

    # Admin - Stores Group

    @_admin.group(name='stores', invoke_without_command=True)
    async def _stores(self, ctx):
        return await ctx.send('available options: add, list, delete')

    @_stores.command(name='add')
    async def _add_store(self, ctx, location_id: int = 1, *, name: str = None):
        if name is not None:
            self.stores.add(name, location_id)
            await ctx.send("{0} has been added.".format(name))

    @_stores.command(name='list')
    async def _list_stores(self, ctx):
        await ctx.trigger_typing()
        stores = self.stores.list()
        embed = discord.Embed(title='Available Stores', description='Some text')
        for store in stores:
            embed.add_field(name=store['name'], value='ID: ' + str(store['id']))
        await ctx.send(embed=embed)

    @_stores.group(name='set', invoke_without_command=True)
    async def _set_stores(self, ctx):
        return await ctx.send('available options: thumbnail')

    @_set_stores.command(name='thumbnail')
    async def _set_store_thumbnail(self, ctx, store_id: int = 0, url: str = None):
        print('thumbnail')
        store = Store(store_id)
        store.set_thumbnail(url)
        return await ctx.send('Set thumbnail')

    # Admin - Locations Group

    @_admin.group(name='locations', invoke_without_command=True)
    async def _locations(self, ctx):
        await ctx.trigger_typing()
        stores = self.locations.list()
        embed = discord.Embed(title='Available Locations', description='Some text')
        for store in stores:
            embed.add_field(name=store['name'], value='ID: ' + str(store['id']))
        await ctx.send(embed=embed)
        # return await ctx.send('available options: add, list, delete')

    @_locations.command(name='add')
    async def _add_location(self, ctx, *, name: str = None):
        if name is not None:
            self.locations.add(name)
            await ctx.send("{0} has been added.".format(name))

    @_admin.command(name='reset_inventory', aliases=['rinv', 'ri'])
    async def _reset_inventory(self, ctx):
        self.c.execute('''DELETE FROM wars_inventory WHERE user=?''', (ctx.message.author.id,))
        self.conn.commit()
        return await ctx.send('Reset Inventory for ' + ctx.message.author.display_name)

    @_admin.command(name='loaddefaults')
    async def _load_defaults(self, ctx):
        with open('defaults.json') as file:
            data = json.load(file)
            stores = data['stores']
            locations = data['locations']
            items = data['items']
            for item in items:
                self.items.new(set_id=item['id'], name=item['name'], emoji=item['emoji'],
                               price_min=item['price_min'], price_max=item['price_max'],
                               description=item['description'])
            for location in locations:
                self.locations.add(location['name'], location['id'])
            for store in stores:
                self.stores.add(name=store['name'],  location_id=store['location_id'], items=store['items'])
        return await ctx.send('Defaults loaded.')

    @_admin.group(name='role', invoke_without_command=True)
    async def _role(self, ctx):
        return await ctx.send('Try add, give, remove, set, list')

    @_role.command(name='add')
    @commands.has_permissions(manage_roles=True)
    async def _add_role(self, ctx, *, role: str = None):
        guild = ctx.guild
        await guild.create_role(name=role)
        return await ctx.send(role + ' role created.')

    @_role.command(name='give')
    @commands.has_permissions(manage_roles=True)
    async def _give_role(self, ctx, member: discord.Member = None, role: str = None):
        role = discord.utils.get(ctx.guild.roles, name=role)
        await member.add_roles(role)
        return await ctx.send(member.display_name + ' given role ' + role.name)

    @commands.command(name='onlyfordoofus')
    @commands.has_role('doofus')
    async def _hi_doofus(self, ctx):
        return await ctx.send('Hi doofus!')


def setup(bot):
    bot.add_cog(Mod(bot))
