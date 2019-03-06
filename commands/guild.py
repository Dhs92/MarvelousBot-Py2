import asyncio
import logging
from datetime import datetime
from datetime import timedelta

import asyncpg
from croniter import croniter
from discord.ext import commands

from utils.config.config import Config

config = Config()


class GuildCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._job_store = 'jobstore'
        self._fired = False
        self.pool: asyncpg.pool = None
        self.bot.loop.create_task(self.connect())
        self.bot.loop.create_task(self.loop())

    # setting up the database and connection
    async def connect(self):
        self.pool = await asyncpg.create_pool(host='localhost',
                                              user=config.db_user,
                                              password=config.db_pass,
                                              database=self._job_store)

        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute('''
                create table if not exists jobs(job_id text primary key NOT NULL,
                                                channel_id bigint NOT NULL,
                                                time timestamp NOT NULL,
                                                msg text default NULL
                                                );
                                        ''')

                await connection.execute('''
                create table if not exists schedule(sched_id text primary key,
                                                    interval text
                                                    );
                ''')

    # loop to check against database
    async def loop(self):
        await asyncio.sleep(10)
        if self.bot.is_ready():
            while not self.bot.is_closed():
                async with self.pool.acquire() as connection:
                    now = datetime.now()
                    result = await connection.fetch("select * from jobs;")

                    for job_id, channel, time, msg in result:
                        if (await self.guild_war_empty(job_id) is not None) \
                                and (time is not None) and (channel is not None):

                            channel = self.bot.get_channel(channel)
                            if time <= now:
                                if job_id is not 'summon_1' and job_id is not 'summon_2':
                                    await channel.send(msg)
                                    await asyncio.sleep(2)
                                    await connection.execute("DELETE FROM jobs WHERE job_id = $1", job_id)

                                    logging.debug(f'ID: {job_id}')
                                    logging.debug(f'Time: {time}')
                                    logging.debug(f'Channel ID: {channel}')

                                elif job_id is 'summoned_1' or job_id is 'summoned_2' and not self._fired:
                                    await channel.send(msg)
                                    await asyncio.sleep(2)
                                    await connection.execute("DELETE FROM jobs WHERE job_id = $1", job_id)
                                    await self.guild_schedule_next()

                                    logging.debug(f'ID: {job_id}')
                                    logging.debug(f'Time: {time}')
                                    logging.debug(f'Channel ID: {channel}')

                                elif job_id is 'summoned_1' or job_id is 'summoned_2' and self._fired:
                                    await connection.execute("DELETE FROM jobs WHERE job_id = $1", job_id)
                                    await self.guild_schedule_next()
                                    self._fired = False

                                    logging.debug(f'ID: {job_id}')
                                    logging.debug(f'Time: {time}')
                                    logging.debug(f'Channel ID: {channel}')
                            else:
                                await asyncio.sleep(15)
                        else:
                            await asyncio.sleep(60)

    async def guild_war_empty(self, job_id):
        async with self.pool.acquire() as connection:
            if await connection.fetchrow("SELECT time FROM jobs where job_id = $1;", job_id) is None:
                return None
            else:
                return 1

    @commands.command(name='tmp')
    async def guild_schedule_next(self, ctx):
        channel = config.channel
        now = datetime.now()
        job_id = ['summon_1', 'summon_2']
        schedule = [croniter('0 06 * * 0,2,4 *', now), croniter('0 18 * * 1,3 *', now)]
        next_run = [schedule[0].get_next(datetime), schedule[1].get_next(datetime)]
        msg = f"<@{config.adminID}>, <@{config.coAdminID}> Don't forget to summon the guild boss!"
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                for job, next_r in zip(job_id, next_run):
                    try:
                        await self.pool.execute('''
                            insert into jobs(job_id, channel_id, time, msg)
                            values($1, $2, $3, $4);
                            ''', job, channel, next_r, msg)
                    except asyncpg.UniqueViolationError:
                        pass

################################# COMMANDS #################################################
############################################################################################

    @commands.group(name='guildwar', aliases=['gw', 'guildw'], invoke_without_command=1)
    @commands.has_any_role(['Guild Master', 'Co Master', 'Veterans'])
    async def guild_war(self, ctx):  # used to create guild war reminder
        await ctx.send('Please enter a sub-command: [add, cancel]')

    @guild_war.command(name='add')
    @commands.has_any_role('Guild Master', 'Co Master', 'Veterans')
    async def guild_war_add(self, ctx, hours: int, minutes: int):

        # get the connection

        if await self.guild_war_empty('gw_sleep') is None:
            now = datetime.now()
            now += timedelta(hours=hours, minutes=minutes)

            logging.debug(f'Now: {now}')

            # store the channel ID from context
            channel = ctx.channel.id

            hours_string = str(hours) + (' hours and ' if hours != 1 else ' hour and ')
            empty = str()
            msg = "@everyone The Guild War has begun!"
            await ctx.send('@everyone The Guild War will start in '
                           f'{hours_string if not hours == 0 else empty}{minutes} '
                           + ('minutes' if minutes != 1 else 'minute'))

            # add job to database
            await self.pool.execute('''
            insert into jobs(job_id, channel_id, time, msg)
            values('gw_sleep', $1, $2, $3);
            ''', channel, now, msg)

        elif await self.guild_war_empty('gw_sleep') is not None:
            await ctx.send('You already set a timer!')
        else:
            pass

    @guild_war.command(name='cancel')
    @commands.has_any_role('Guild Master', 'Co Master', 'Veterans')
    async def guild_war_rm(self, ctx):
        with self.pool.acquire() as connection:
            if await self.guild_war_empty('gw_sleep') is not None:
                await connection.execute("DELETE FROM jobs WHERE job_id = 'gw_sleep';")
                await ctx.send('Guild war reminder cancelled')
            else:
                await ctx.send('You haven\'t set a reminder yet!')

    @commands.group(name='summoned', invoke_without_command=1)
    @commands.has_any_role('Guild Master', 'Co Master')
    async def guild_summoned(self, ctx):
        if not self._fired:
            await ctx.send('@everyone The guild boss has been summoned!')
            self._fired = True
        else:
            await ctx.send('You have already marked the guild boss as summoned!')

    @guild_summoned.command(name='cancel')
    @commands.has_any_role('Guild Master', 'Co Master')
    async def guild_summoned_cancel(self, ctx):
        if self._fired:
            await ctx.send('False alarm!')
            self._fired = False
        else:
            await ctx.send("You haven't marked the guild boss as summoned yet!")


def setup(bot):
    bot.add_cog(GuildCommands(bot))
