import logging
import os

import discord
from discord.ext import commands

from config.config import Config

bot = commands.Bot(command_prefix='?')
config = Config()


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    logging.info(f'Version: {discord.__version__}')

    game = discord.Game(name='Grand Chase Dimensional Chasers')
    await bot.change_presence(activity=game)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    initial_extensions = ['commands.' + i.split('.')[0] for i in os.listdir('commands') if '.py' in i]
    logging.info(f'Extensions: {initial_extensions}')
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            logging.info(f'Failed to load extension {extension}')


bot.run(config.token, bot=True, reconnect=True)
