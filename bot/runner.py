
# Entry point for server

import os, logging, asyncio

from discord.ext import commands
from dotenv import load_dotenv

from bot.tools.util import path_resolve
from .commands import Games
from .config import Config

class Runner:

    def __init__(self) -> None:
        pass

    def run(self):

        # first (and only) config load
        config = Config()

        # first-time logger setup
        logger = self.__get_logger(config.log_name, level=config.log_level, showname=config.log_showname)

        logger.info(f'Loaded games: {", ".join(config.game_lib.keys())}')

        logger.debug('Creating bot...')

        # environment variables
        load_dotenv()
        token = os.getenv('BOT_TOKEN')

        # create bot
        bot = commands.Bot(command_prefix=config.bot_prefix)
        bot.add_cog(Games(bot))

        # run bot coroutines
        loop = asyncio.get_event_loop()
        try:
            logger.info('Starting...')
            loop.run_until_complete(bot.start(token))
        except KeyboardInterrupt:
            logger.debug('Signal to stop bot!')
            loop.run_until_complete(bot.close())

        # close and exit
        logger.debug('Closed bot and event loop.')
        logger.info('Exiting.\n\n')

        return 0


    # Create logger and configure
    def __get_logger(self, name, level=logging.INFO, showname=False):
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

        logger.addHandler(console_handle)
        logger.addHandler(file_handle)

        return logger
