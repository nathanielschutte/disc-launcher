
# Discord Cog - handle commands

import asyncio
import logging

import discord
from discord.ext import commands

from bot.launcher import DiscLauncher
from .tools.events import Events
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

        # get logger
        self.logger = logging.getLogger(self.config.log_name)

        self.lock = asyncio.Lock()


    # ===========================================
    # Internal functions
    # TODO use discord command checks
    # Validate request server (whitelist)
    def __validate(self, ctx: commands.Context, allowed_in_game=False) -> bool:
        server = ctx.guild.name
        author_id = ctx.message.author.id
        message = ctx.message.content
        if not self.config.use_whitelist or server in self.config.whitelist:
            if message.strip().startswith(self.config.bot_prefix):
                command = message.strip().split(self.config.bot_prefix)[1].split()[0]

                # TODO check against roles config
                # temp...just check IDs for non-any commands
                if self.config.commands[command]['permission'] != 'any':
                    if author_id != 239605736030601216:
                        self.logger.warning(f'User \'{author_id}\' tried to use admin command: {command}')
                        return False

                # In game
                if ctx.guild.id in self.launchers and ctx.channel.id in self.launchers[ctx.guild.id].games:
                    return allowed_in_game

            return True

        else:
            self.logger.warning(f'Server \'{server}\' tried to use this bot!')
            return False

    # # Internal tick (wide interval)
    # async def __tick_loop(self):
    #     while True:
    #         await asyncio.sleep(10)
    #         self.events.emit('tick')

    # # Periodically check for dead launchers and remove them
    # async def __clean_launchers(self):
    #     self.logger.debug('Looking for dead launchers...')
    #     async with self.lock:
    #         for name, launcher in self.launchers:
    #             if launcher.dead:
    #                 self.logger.debug('Found dead launcher [{launcher.name}], terminating')
    #                 launcher.clean()
    #                 del self.launchers[name]

    # ===========================================
    # General listeners
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('Bot is ready!')

    @commands.Cog.listener()
    async def on_message(self, msg):

        # ignore bot messages
        if msg.author.id == self.bot.user.id:
            return

        # intercept game messages
        if msg.guild.id in self.launchers:
            if self.launchers[msg.guild.id].get_game(msg.channel.id):

                # handle non-bot commands
                if not msg.content.strip().startswith(self.config.bot_prefix):

                    # send message along to launcher
                    self.logger.debug(f'GAME MSG| server: {msg.guild.name} channel: {msg.channel.id} | {msg.content}') 
                    await self.launchers[msg.guild.id].game_message(msg.channel.id, msg.author.id, msg.content)   
                
                # remove the message
                await msg.delete()

    @commands.Cog.listener()
    async def on_disconnect(self):
        pass

    @commands.Cog.listener()
    async def on_error(self):
        pass


    # ===========================================
    # Game commands
    @commands.command()
    async def play(self, ctx: commands.Context, *game):
        if not self.__validate(ctx):
            return

        # Check input format
        if len(game) == 0:
            await ctx.send('Please specify the game you want to play.')
            return

        game_ref = ' '.join(game)

        # Start up new launcher for this server
        async with self.lock:
            if ctx.guild.id not in self.launchers:
                self.logger.info(f'No existing launcher for guild \'{ctx.guild.name}\' - creating launcher')
                self.launchers[ctx.guild.id] = DiscLauncher(ctx.bot, ctx.channel.name)

            launcher: DiscLauncher = self.launchers[ctx.guild.id]

            # Tell launcher to start the referenced game
            try:
                await launcher.start_game(ctx.channel.id, ctx.author.id, game_ref)
            except GameAlreadyRunningException as e:
                self.logger.debug(str(e))
            except InvalidGameException as e:
                await ctx.send(f'The game \'{game_ref}\' isn\'t in my library.')
                return

    @commands.command()
    async def end(self, ctx: commands.Context):
        if not self.__validate(ctx, allowed_in_game=True):
            return

        # Check for launcher
        if ctx.guild.id not in self.launchers:
            self.logger.debug(f'No existing launcher for guild \'{ctx.guild.name}\' - do nothing')
            return

        launcher: DiscLauncher = self.launchers[ctx.guild.id]
        self.logger.info(f'Attempting to end game in channel {ctx.channel.id}: {launcher.get_game(ctx.channel.id).title}')

        await launcher.end_game(ctx.channel.id, ctx.author.id)


    @commands.command()
    async def join(self, ctx: commands.Context):
        if not self.__validate(ctx):
            return

    @commands.command()
    async def leave(self, ctx):
        if not self.__validate(ctx, allowed_in_game=True):
            return

    @commands.command()
    async def list(self, ctx: commands.Context):
        if not self.__validate(ctx):
            return

        game_list = self.config.game_lib.keys()
        await ctx.send('Games: ' + ', '.join(game_list))


    # Admin commands
    # Reload config, which means reloading the game library
    @commands.command()
    async def reload(self, ctx: commands.Context):
        if not self.__validate(ctx):
            return

        self.logger.info('Reloading bot config...')

        self.config.load()

        self.logger.info('Done')



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

                embed = discord.Embed(title=f'{self.config.bot_title} help:')

                for cmd in mapping[cog]:

                    # Skip commands that have a permission besides 'any'
                    if cmd.name in self.config.commands \
                            and 'permission' in self.config.commands[cmd.name] \
                            and self.config.commands[cmd.name]['permission'] != 'any':
                        
                        continue
                    
                    cmdinfo = self.__cmdinfo(cmd.name)

                    astr = ''
                    if len(cmdinfo['aliases']) > 0:
                        astr = ' (aka ' + ', '.join(cmdinfo['aliases']) + ')'

                    cmdstr = f'{cmdinfo["desc"]}\n`{self.config.bot_prefix}{cmd.name} {cmdinfo["usage"]}`'
                    embed.add_field(name=f'{cmd.name}:', value=cmdstr, inline=False)

                
                await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        return await super().send_group_help(group)

    async def send_command_help(self, command):
        return await super().send_command_help(command)
