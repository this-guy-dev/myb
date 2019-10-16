import discord

# noinspection PyPackageRequirements
from discord.ext import commands
from src.models.player import Player
from src.models.location import Location
from src.models.store import Store
from src.models.store import StoreManager
from src.models.item import ItemManager
from src.models.item import Item


class Stores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stores = StoreManager()
        self.items = ItemManager()

    @commands.group(name='store', invoke_without_command=True)
    async def _store(self, ctx):
        """View store information and inventory."""
        player = Player(ctx.message.author.id)
        location = Location(player.current_location)
        store_ids = self.stores.list_id()
        for store_id in store_ids:
            store = Store(store_id)
            prices = store.settings['prices']
            if store.location.location_id == player.current_location:
                embed = discord.Embed(
                    title=location.name,
                    color=discord.Color.green(),
                    description='Welcome to **' + store.name + '**, ' + ctx.message.author.display_name + '!')
                items = self.items.list()
                embed.add_field(name='Items for Sale', value='The following are available for sale.\n', inline=False)
                for item in items:
                    if item['id'] in store.available_items:
                        embed.add_field(
                            name=item['emoji'] + ' ' + str(item['id']) + '. ' + item['name'],
                            value='Price: ' + str(prices[str(item['id'])])
                        )
                embed.set_footer(text='Requested by '+ctx.message.author.display_name + '. Prices updated: '
                                      + str(prices['date']),
                                 icon_url=ctx.message.author.avatar_url)
                if hasattr(store, 'thumbnail'):
                    embed.set_thumbnail(url=store.thumbnail)
                await ctx.send(embed=embed)

    @_store.command(name='buy')
    async def _buy_item(self, ctx, item_id: int = 0, count: int = 0):
        """Buy an item from the store."""
        item_object = Item(item_id)
        cost = item_object.get_price() * count
        player = Player(ctx.message.author.id)
        balance = player.get_balance()
        wallet = balance['wallet']
        if cost > wallet:
            return await ctx.send("Not enough cash. Need: " + str(cost))
        else:
            player.add_balance('wallet', -cost)
            player.add_to_inventory(item_id, count)
            return await ctx.send("Successfully purchased.")


def setup(bot):
    bot.add_cog(Stores(bot))