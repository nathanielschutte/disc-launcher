
# Discord Cog - handle commands

import logging
from pydoc import describe

import discord
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


    # ===========================================
    # Internal functions

    # Validate request server (whitelist)
    def __validate(self, server):
        if not self.config.use_whitelist or server in self.config.whitelist:
            return True
        else:
            self.logger.warning(f'Server \'{server}\' tried to use this bot!')

    # Get help string for command
    def __gethelp(self, cmd):
        if cmd in self.config.help:
            return self.config.help[cmd]
        else:
            return ''


    # ===========================================
    # General listeners
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.debug('Bot is ready!')

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not self.__validate(msg.guild.name):
            return
        #self.logger.debug(f'Received message from {msg.author.name}: {msg.content}')


    # ===========================================
    # Game commands
    @commands.command()
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

    @commands.command()
    async def end(self, ctx):
        pass

    @commands.command()
    async def join(self, ctx):
        pass

    @commands.command()
    async def leave(self, ctx):
        pass

    @commands.command()
    async def list(self, ctx):
        game_list = self.config.game_lib.keys()
        await ctx.send('Games: ' + ', '.join(game_list))



class GamesHelp(commands.HelpCommand):
    '''Bot commands help'''

    def __init__(self):
        super().__init__()
        
        self.indent = 4
        self.config = Config()

    def __cmdinfo(self, cmd):
        if cmd in self.config.commands:
            return self.config.commands[cmd]
        else:
            return {
                'aliases': [],
                'desc': '',
                'usage': '',
            }

    async def send_bot_help(self, mapping):
        for cog in mapping:
            if cog is not None and hasattr(cog, 'qualified_name') and cog.qualified_name == 'Games':
                cmdlist = []

                for cmd in mapping[cog]:
                    cmdinfo = self.__cmdinfo(cmd.name)

                    astr = ''
                    if len(cmdinfo['aliases']) > 0:
                        astr = '(' + ' | '.join(cmdinfo['aliases']) + ')'

                    cmdlist.append(f'{" "*self.indent}{cmd.name} {astr}: {" "*self.indent}{cmdinfo["desc"]}{" "*self.indent}|{" "*self.indent}usage: {cmd.name} {cmdinfo["usage"]}')
                
                cmdstr = '\n'.join(cmdlist)
                embed = discord.Embed(title=f'{self.config.bot_title} help:', description=cmdstr)
                await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        return await super().send_group_help(group)

    async def send_command_help(self, command):
        return await super().send_command_help(command)
