import logging

from discord.ext import commands


class GuildBoss:
    def __init__(self, bot):
        self.bot = bot
        self.__summoned__ = False

    @commands.command()
    async def summoned(self, ctx):
        self.__summoned__ = True
        logging.info(f'Bot has been marked as summoned by {ctx.author.id}')


def setup(bot):
    bot.add_cog(GuildBoss(bot))
