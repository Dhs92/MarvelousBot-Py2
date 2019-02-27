import asyncio
import logging
import typing
from datetime import datetime

import pytz
from discord.ext import commands

from commands.utils.checks import is_admin
from config.config import Config

config = Config()


class GuildBoss(commands.Cog):
    def __init__(self, bot):
        self.timezone = pytz.timezone("America/New_York")
        self.now = datetime.now().astimezone(self.timezone) # make `now` timezone aware
        self.bot = bot
        self.__summoned__ = False

    @commands.command()
    @is_admin(commands, config)
    async def summoned(self, ctx, arg: typing.Optional[str] = ''):

        if arg.lower() == "undo" and self.__summoned__:
            await ctx.send(f"False alarm")
            self.__summoned__ = False

        elif arg.lower() == "undo" and not self.__summoned__:
            await ctx.send("The boss hasn't been marked as summoned yet!")

        elif not self.__summoned__:
            self.__summoned__ = True
            await ctx.send("@everyone Guild Boss has been summoned")
            logging.info(f"Boss has been marked as summoned by {ctx.author.name}")

        elif self.__summoned__:
            await ctx.send(f"The boss has already been summoned, {ctx.author.name}")

        else:
            logging.info("An unknown exception has occurred in `summoned`")

    @summoned.error
    async def summon_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to run this command!')

    async def schedule_message(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(int(config.channel))
        self.bot.fired = False

        while not self.bot.is_closed():
            self.bot.fired = False 

            if self.bot.summoned:  # if the summoned command is run, sleep until out of range
                await asyncio.sleep(28800)
                self.bot.summoned = False
            elif (self.now.hour == 12) and (self.now.weekday() == 1 or self.now.weekday() == 3) \
                    and not self.bot.summoned:
                await channel.send(f"<@{config.adminID}>, <@{config.coAdminID}> Don't forget to summon the guild boss!")
                self.bot.fired = True

            elif (self.now.hour == 23) and (
                    self.now.weekday() == 0 or self.now.weekday() == 2 or self.now.weekday() == 4) \
                    and not self.bot.summoned:
                await channel.send(f"<@{config.adminID}>, <@{config.coAdminID}> Don't forget to summon the guild boss!")
                self.bot.fired = True

            if self.bot.fired:  # if message has fired, sleep until out of range
                await asyncio.sleep(28800)  # 8 hours
                self.bot.fired = False

            await asyncio.sleep(900)  # 15 minutes


def setup(bot):
    bot.add_cog(GuildBoss(bot))
