
# Game launcher - handle games

import os, logging, asyncio

from discord.ext import commands
from dotenv import load_dotenv

from bot.tools.util import path_resolve
from .commands import Games
from .config import Config



class DiscLauncher:
    
    def __init__(self) -> None:
        pass

    def test(self):
        print('hello')



class Runner:

    def __init__(self) -> None:
        pass

    def run(self):

        config = Config()
        launcher = DiscLauncher()

        logger = self.__get_logger(config.log_name, config.log_showname)

        logger.debug('Loading env and config...')

        load_dotenv()
        token = os.getenv('BOT_TOKEN')

        bot = commands.Bot(command_prefix=config.bot_prefix)

        bot.add_cog(Games(bot, launcher))

        # Run bot coroutines
        loop = asyncio.get_event_loop()
        try:
            logger.info('Starting...')
            loop.run_until_complete(bot.start(token))
        except KeyboardInterrupt:
            logger.debug('Signal to stop bot, closing...')
            loop.run_until_complete(bot.close())

        logger.debug('Closed bot and event loop')
        logger.info('Exiting\n\n')

        return 0


    def __get_logger(self, name, showname):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

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
