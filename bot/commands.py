
# Discord Cog - handle commands

import logging

from discord.ext import commands

from bot.launcher import DiscLauncher
from .config import Config
from .exceptions import *


class Games(commands.Cog):
    '''Game commands'''

    def __init__(self, bot) -> None:
        super().__init__()
        
        # reference to discord bot object
        self.bot = bot

        # get config
        self.config = Config()

        # game controllers per server
        self.launchers = {}

        # retrieve config instance
        self.logger = logging.getLogger(self.config.log_name)


    # Internal functions
    def __validate(self, server):
        if server in self.config.whitelist:
            return True
        else:
            self.logger.warning(f'Server \'{server}\' tried to use this bot!')


    # General listeners
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug('Bot is ready!')

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not self.__validate(msg.guild.name):
            return
        #self.logger.debug(f'Received message from {msg.author.name}: {msg.content}')


    # ================================
    #           Game commands 
    # ================================
    @commands.command(help='')
    async def play(self, ctx, *game):
        if not self.__validate(ctx.guild.name):
            return

        # Check input format
        if len(game) == 0:
            await ctx.send('Please specify the game you want to play.')
            return

        game_ref = game[0]

        # Start up new launcher for this server
        if ctx.guild.id not in self.launchers:
            self.logger.debug(f'No existing launcher for guild \'{ctx.guild.name}\' - creating launcher')
            self.launchers[ctx.guild.id] = DiscLauncher() 

        launcher: DiscLauncher = self.launchers[ctx.guild.id]

        # Tell launcher to start the referenced game
        try:
            launcher.start_game(ctx.channel.id, ctx.author.id, game_ref)
        except GameAlreadyRunningException as e:
            self.logger.warning(str(e))
        except InvalidGameException as e:
            await ctx.send(f'The game \'{game_ref}\' isn\'t in my library.')
            return
            

