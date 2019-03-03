import asyncio
import logging
from datetime import datetime
from datetime import timedelta

import asyncpg
from discord.ext import commands

from utils.config.config import Config

config = Config()


class GuildCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._job_store = 'jobstore'
        self._timer = None
        self._fired = False
        self.bot.loop.create_task(self.loop())

    # setting up the database and connection
    async def connect(self) -> asyncpg.connection:
        connection = await asyncpg.connect(host='localhost',
                                           user=config.db_user,
                                           password=config.db_pass,
                                           database=self._job_store)
        await connection.execute('''
        create table if not exists jobs(job_id text primary key,
                                        channel_id bigint,
                                        time timestamp
                                        );
                                ''')

        return connection

    # TODO add check for summoned command
    # loop to check against database
    async def loop(self):
        connection = await self.connect()

        while not self.bot.is_closed():
            now = datetime.now()
            timer = await connection.fetchval("SELECT time FROM jobs WHERE job_id = 'gw_sleep'")
            channel = await connection.fetchval("SELECT channel_id FROM jobs WHERE job_id = 'gw_sleep'")
            channel = self.bot.get_channel(channel)

            if (await self.guild_war_empty(connection) is not None) and (timer is not None) and (channel is not None):
                if timer <= now:
                    await channel.send('@everyone Guild war has started!')
                    await asyncio.sleep(2)
                    await connection.execute("DELETE FROM jobs WHERE job_id = 'gw_sleep'")
                else:
                    await asyncio.sleep(60)

################################# COMMANDS #################################################
############################################################################################
    @commands.group(name='guildwar', aliases=['gw', 'guildw'], invoke_without_command=1)
    @commands.has_any_role(['Guild Master', 'Co Master', 'Veterans'])
    async def guild_war(self, ctx):  # used to create guild war reminder
        await ctx.send('Please enter a sub-command: [add, cancel]')

    async def guild_war_empty(self, connection: asyncpg.Connection):
        if await connection.fetchrow("SELECT time FROM jobs where job_id = 'gw_sleep';") is None:
            return None
        else:
            return 1

    @guild_war.command(name='add')
    @commands.has_any_role(['Guild Master', 'Co Master', 'Veterans'])
    async def guild_war_add(self, ctx, hours: int, minutes: int):

        # get the connection
        connection = await self.connect()

        if await self.guild_war_empty(connection) is None:
            now = datetime.now()
            now += timedelta(hours=hours, minutes=minutes)

            logging.debug(f'Now: {now}')

            # store the channel ID from context
            channel = ctx.channel.id

            hours_string = str(hours) + (' hours and ' if hours != 1 else ' hour and ')
            empty = str()

            await ctx.send('@everyone Guild war will start in '
                           f'{hours_string if not hours == 0 else empty}{minutes} '
                           + ('minutes' if minutes != 1 else 'minute'))

            # add job to database
            await connection.execute('''
            insert into jobs(job_id, channel_id, time)
            values('gw_sleep', $1, $2);
            ''', channel, now)

        elif await self.guild_war_empty(connection) is not None:
            await ctx.send('You already set a timer!')
        else:
            pass

        await connection.close()

    @guild_war.command(name='cancel')
    @commands.has_any_role(['Guild Master', 'Co Master', 'Veterans'])
    async def guild_war_rm(self, ctx):
        connection = await self.connect()

        if await self.guild_war_empty(connection) is not None:
            await connection.execute("DELETE FROM jobs WHERE job_id = 'gw_sleep';")
            await ctx.send('Guild war reminder cancelled')
        else:
            await ctx.send('You haven\'t set a reminder yet!')

        await connection.close()

    # TODO add next job to db on execute
    @commands.group(name='summoned', invoke_without_command=1)
    @commands.has_any_role(['Guild Master', 'Co Master'])
    async def guild_summoned(self, ctx):
        if not self._fired:
            await ctx.send('@everyone The guild boss has been summoned!')
            self._fired = True
        else:
            await ctx.send('You have already marked the guild boss as summoned!')

    @guild_summoned.command(name='cancel')
    @commands.has_any_role(['Guild Master', 'Co Master'])
    async def guild_summoned_cancel(self, ctx):
        if self._fired:
            await ctx.send('False alarm!')
            self._fired = False
        else:
            await ctx.send("You haven't marked the guild boss as summoned yet!")


def setup(bot):
    bot.add_cog(GuildCommands(bot))

