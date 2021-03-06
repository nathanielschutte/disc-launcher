
# Entry point for server

import os, logging, asyncio

from discord.ext import commands
from dotenv import load_dotenv

from bot.tools.util import path_resolve
from bot.tools import events
from .exceptions import ConfigLoadError
from .commands import Games, GamesHelp
from .config import Config

class Runner:

    def __init__(self) -> None:
        pass

    def run(self):

        # first (and only) config instance
        try:
            config = Config()
        except ConfigLoadError as e:
            print(f'Issue loading config!  {str(e)}')
            return 1

        # first-time logger setup
        logger = self.__get_logger(config.log_name, level=config.log_level, showname=config.log_showname, stdout=config.stdout)
    
        logger.info('Starting...')
        logger.info(f'Loaded games: {", ".join(config.game_lib.keys())}')

        logger.debug('Creating bot...')

        # environment variables
        load_dotenv()
        token = os.getenv('BOT_TOKEN')

        # create bot
        bot = commands.Bot(command_prefix=config.bot_prefix, help_command=GamesHelp())
        bot.add_cog(Games(bot))

        # run bot coroutines
        loop = asyncio.get_event_loop()
        try:
            logger.info(f'Waking up bot with prefix \'{config.bot_prefix}\'...')
            loop.run_until_complete(bot.start(token))

        # signal interrupts should kill it
        except KeyboardInterrupt:
            logger.debug('Signal to stop bot!')
            loop.run_until_complete(bot.close())

        # anything else unknown
        except Exception as e:
            logger.error(f'Exception: {str(e)}')

        # close and exit
        logger.debug('Closed bot and event loop.')
        logger.info('Exiting.\n\n')

        return 0


    # Create logger and configure
    def __get_logger(self, name, level=logging.INFO, showname=False, stdout=True):
        logger = logging.getLogger(name)
        logger.setLevel(level)

        console_handle = logging.StreamHandler()
        console_handle.setLevel(logging.DEBUG)
        file_handle = logging.FileHandler(path_resolve('out.log', force_exists=False), encoding='utf-8')

        if showname:
            formatter = logging.Formatter('%(asctime)s - %(name)s [%(levelname)s] |   %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] |   %(message)s')
        console_handle.setFormatter(formatter)
        file_handle.setFormatter(formatter)

        if stdout:
            logger.addHandler(console_handle)

        logger.addHandler(file_handle)

        return logger
