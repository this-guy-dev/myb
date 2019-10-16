import discord
import time

# noinspection PyPackageRequirements
from discord.ext import commands
from src.models.player import Player
from src.models.store import StoreManager
from src.models.location import Location
from src.models.location import LocationManager


class Subway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stores = StoreManager()
        self.locations = LocationManager()

    @commands.group(name='subway', invoke_without_command=True)
    async def _subway(self, ctx, location_id: int = 0):
        """Use map to view station map, or an id to move to another station."""
        await ctx.trigger_typing()
        if not location_id:
            return await ctx.send('Try either map or a valid location id.')
        player = Player(ctx.message.author.id)
        if player.current_location == location_id:
            return await ctx.send('You are already there.')
        distance = abs(location_id - player.current_location)
        current_location = Location(player.current_location)
        await ctx.send(':train: ' + ctx.message.author.display_name + ' is now leaving: **' + current_location.name
                       + '** :train:')
        player.move_to(location_id)
        location = Location(location_id)
        time.sleep(distance)
        return await ctx.send(':train: ' + ctx.message.author.display_name + ' is now arriving at: **' + location.name + '** :train:')

    @_subway.command(name='map', aliases=['stops'])
    async def _subway_maps(self, ctx):
        """View a map of this system's stations."""
        await ctx.trigger_typing()
        player = Player(ctx.message.author.id)
        current_location = Location(player.current_location)
        locations = self.locations.list()
        stops_str = ''
        for location in locations:
            if location['id'] == player.current_location:
                stops_str = stops_str + ':small_orange_diamond: '
            else:
                stops_str = stops_str + ':small_blue_diamond: '
            stops_str = stops_str + str(location['id']) + '. ' + location['name']
            stores = self.stores.at_location(location['id'])
            if len(stores) > 0:
                stores_str = ' ('
                for store in stores:
                    stores_str = stores_str + store.name
                    if store != stores[-1]:
                        stores_str = stores_str + ', '
                stops_str = stops_str + stores_str
                stops_str = stops_str + ')'
            stops_str = stops_str + '\n'
        guild = ctx.message.guild.name
        embed = discord.Embed(
            title='Subway Stops',
            color=discord.Color.blurple(),
            description='Map of ' + guild + '\nYou are currently in ' + current_location.name
        )
        embed.set_footer(text='Queried by ' + ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        embed.add_field(name='Stops', value=stops_str)
        embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/MBTA.svg/1200px-MBTA.svg.png')
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Subway(bot))
