import asyncio
import logging
import typing
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

from utils.checks import is_admin
from utils.config.config import Config

config = Config()


class Guild(commands.Cog):
    def __init__(self, bot):
        self.timezone = pytz.timezone('America/New_York')
        self.now = datetime.now().astimezone(self.timezone) # make `now` timezone aware
        self.bot = bot
        self._summoned = False
        self._delay = 0
        self._timer = AsyncIOScheduler()
        self._timer.start()

    @commands.command(aliases=['summon', 'boss', 'gb'])
    @is_admin(commands, config)
    async def summoned(self, ctx, arg: typing.Optional[str] = ''):

        if arg.lower() == 'undo' and self._summoned:
            await ctx.send('False alarm')
            self._summoned = False

        elif arg.lower() == 'undo' and not self._summoned:
            await ctx.send('The boss hasn\'t been marked as summoned yet!')

        elif not self._summoned:
            self._summoned = True
            await ctx.send('@everyone Guild Boss has been summoned')
            logging.info(f'Boss has been marked as summoned by {ctx.author.name}')

        elif self._summoned:
            await ctx.send(f'The boss has already been summoned, {ctx.author.name}')

        else:
            logging.info('An unknown exception has occurred in `summoned`')

    @summoned.error
    async def summon_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have permission to run this command!')

    @commands.command(aliases=['gw', 'guildw', 'guildwar'])
    @is_admin(commands, config)
    async def guild_war(self, ctx, hours: typing.Optional[int] = 0, minutes: typing.Optional[int] = 0,
                        cancel: str = ''):

        async def guild_war_message():
            await ctx.send('@everyone Guild war has started!')

        if cancel.lower() == 'cancel' and not self._delay == 0:
            self._timer.remove_job(job_id='gw_sleep')
            await ctx.send('Cancelled guild war timer')
            self._delay = 0

        elif cancel.lower() == 'cancel' and self._delay == 0:
            await ctx.send('You haven\'t set a guild war timer yet!')

        elif hours == 0 and minutes == 0 and cancel.lower() != 'cancel':
            await ctx.send('Please enter a time in hours and minutes! (eg. `?guildwar 10 30`)')

        elif self._delay == 0 and not cancel.lower == 'cancel':
            self._delay = 0
            self._delay += hours * 3600
            self._delay += minutes * 60
            hours_string = str(hours) + (' hours and ' if hours != 1 else ' hour and ')
            empty = str()
            await ctx.send('@everyone Guild war will start in '
                           f'{hours_string if not hours == 0 else empty}{minutes} '
                           + ('minutes' if minutes != 1 else 'minute'))
            self._timer.add_job(guild_war_message, trigger='interval', id='gw_sleep', seconds=self._delay)
            await asyncio.sleep(self._delay + 10)
            self._timer.remove_job('gw_sleep')
        else:
            await ctx.send('Fuck something went wrong')

    @guild_war.error
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
                await asyncio.sleep(28800) # 8 hours
                self.bot.summoned = False

            elif (self.now.hour == 12) and (self.now.weekday() == 1 or self.now.weekday() == 3) \
                    and not self.bot.summoned:
                await channel.send(f'<@{config.adminID}>, <@{config.coAdminID}> Don\'t forget to summon the guild boss!')
                self.bot.fired = True

            elif (self.now.hour == 23) and (
                    self.now.weekday() == 0 or self.now.weekday() == 2 or self.now.weekday() == 4) \
                    and not self.bot.summoned:
                await channel.send(f'<@{config.adminID}>, <@{config.coAdminID}> Don\'t forget to summon the guild boss!')
                self.bot.fired = True

            if self.bot.fired:  # if message has fired, sleep until out of range
                await asyncio.sleep(28800)  # 8 hours
                self.bot.fired = False

            await asyncio.sleep(900)  # 15 minutes


def setup(bot):
    bot.add_cog(Guild(bot))
