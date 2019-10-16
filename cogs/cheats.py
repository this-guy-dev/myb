import discord

# noinspection PyPackageRequirements
from discord.ext import commands
from src.models.player import Player
from src.models.item import Item


class Cheats(commands.Cog):
    @commands.group(name='add', invoke_without_command=True, hidden=True)
    async def _add_command(self, ctx):
        await ctx.send('Try `add money` or `add item`')

    @_add_command.command(name='item')
    async def _add_item_to_inventory(self, ctx, item_id: int = 0, count: int = 0):
        """Add any item to inventory"""
        player = Player(ctx.message.author.id)
        player.add_to_inventory(item_id, count)
        item_object = Item(item_id)
        await ctx.send(str(count) + ' of ' + item_object.name + ' added to inventory')

    @_add_command.group(name='money', invoke_without_command=True)
    async def _money(self, ctx):
        """Add money, needs wallet or bank."""
        await ctx.send('Try `add money wallet` or `add money bank`')

    @_money.command(name='wallet')
    async def _add_wallet(self, ctx, money: int = 0):
        """Add money to wallet."""
        player = Player(ctx.message.author.id)
        player.add_balance('wallet', money)
        return await ctx.send(str(money) + ' added to wallet.')

    @_money.command(name='bank')
    async def _add_bank(self, ctx, money: int = 0):
        """Add money to bank"""
        player = Player(ctx.message.author.id)
        player.add_balance('bank', money)
        return await ctx.send(str(money) + ' added to bank.')


def setup(bot):
    bot.add_cog(Cheats(bot))
