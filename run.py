import sys
import traceback
# noinspection PyPackageRequirements
from discord.ext import commands

EXTENSIONS = ['main', 'mod', 'subway', 'cheats', 'stores']


class MyBBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?',
                         description="Better than the last one",
                         help_attrs=dict(hidden=True))
        # noinspection SpellCheckingInspection
        self.token = ''

        for extension in EXTENSIONS:
            self.load_extension('cogs.'+extension)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(
                f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    async def on_ready(self):
        print('We have logged in as ' + self.user.name)

    def run(self):
        super().run(self.token, reconnect=True)


if __name__ == '__main__':
    mybbot = MyBBot()
    mybbot.run()
