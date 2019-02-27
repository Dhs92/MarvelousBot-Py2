from discord.ext import commands

from commands.utils.checks import is_owner
from config.config import Config

config = Config()


class OwnerCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='quit', aliases=['close', 'poweroff'])
    @is_owner(commands, config)
    async def bot_quit(self, ctx):
        await ctx.send("Powering off...")
        await self.bot.close()


def setup(bot):
    bot.add_cog(OwnerCommands(bot))
