from discord.ext import commands

from utils.config.config import Config

config = Config()


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(alias=['h'])
    async def help(self, ctx):
        await ctx.send('Test')


def setup(bot):
    bot.add_cog(Help(bot))
