
# Game launcher - handle games for a discord server

import logging, asyncio

from datetime import datetime

from .tools.events import Events
from .config import Config
from .exceptions import GameAlreadyRunningException, InvalidGameException

from discgame import DiscGame, DiscGameMonitor

class DiscGameInstance:
    ''''''

    def __init__(self, host, data, bot, text_channel) -> None:
        
        self.host = host                    # user ID of game host (starter)
        self.title = data['title']          # title from config
        self.ref = data['ref']              # reference keyword from config
        self.path = data['path']            # source path from config
        self.cls = data['class']            # DiscGame object specifier from config

        # DiscGameMonitor used to update screen
        self.monitor: DiscGameMonitor = DiscGameMonitor(bot, text_channel)

        # DiscGame object
        self.game: DiscGame = data['object'](self.monitor)          


    async def startup(self):
        await self.monitor.send('Starting game...')
        await self.game._start_interal()

    async def shutdown(self):
        await self.game._end_internal()
        await self.monitor.clean()


class DiscLauncher:
    
    def __init__(self, bot, name) -> None:
        
        self.config = Config()
        self.logger = logging.getLogger(self.config.log_name)

        self.name = name
        self.running = True
        self.start_time = datetime.now()
        self.restart_time = self.start_time
        self.idle_time = -1
        self.dead = False

        # Game data per channel
        self.games = {} # channel_id: DiscGameInstance

        # Bot context
        self.bot = bot

        # Events
        self.events = Events()
        self.lock = asyncio.Lock()
        self.wake()


    # ===========================================
    # Events
    async def update_loop(self):
        min_counter = 0
        while(self.running):
            await asyncio.sleep(1)

            # emit to all games that a second has passed
            self.events.emit('second')

            # check launcher idle time
            if self.idle_time == -1:
                if len(self.games) == 0:
                    self.idle_time = datetime.now()
            else:
                if len(self.games) > 0:
                    self.idle_time = -1
                    self.dead = False
                else:
                    total_idle = (datetime.now() - self.idle_time).total_seconds()
                    if total_idle >= self.config.launcher_idle_timeout:
                        if not self.dead:
                            self.logger.info(f'Launcher [{self.name}] has been idle for {self.config.launcher_idle_timeout} seconds, marked as dead')
                            self.dead = True

                            # hibernate the launcher
                            self.hibernate()
                            return
            
            min_counter += 1
            if min_counter >= 59:

                # emit to all games that a minute has passed
                self.events.emit('minute')
                min_counter = 0

    async def _every_minute(self):
        self.logger.debug(f'Launcher [{self.name}] has been alive for {(datetime.now() - self.restart_time).total_seconds():.1f} seconds')
    
    async def _every_second(self, value=None):
        pass


    # ===========================================
    # Launcher attributes
    # Get all active DiscGameInstances
    def get_all_games(self):
        return self.games

    # Get DiscGameInstance by channel
    def get_game(self, channel_id) -> DiscGameInstance:
        if channel_id in self.games:
            return self.games[channel_id]
        else:
            return None

    # Get the game library
    def get_library(self):
        return self.config.game_lib

    # Check if game reference exists
    def valid_game_ref(self, game_ref):
        return game_ref in self.get_library()

    # ===========================================
    # Events from bot
    # Start a new game
    async def start_game(self, channel_id, user_id, game_ref):

        if self.dead:
            self.wake()

        # check for existing game
        if self.get_game(channel_id) is not None:
            raise GameAlreadyRunningException(f'Channel {channel_id} has a game already running')

        # check if the game exists in library
        if not self.valid_game_ref(game_ref):
            raise InvalidGameException(None)

        # set game data
        game_data = self.config.game_lib[game_ref]
        text_channel = self.bot.get_channel(channel_id)

        self.logger.info(f'Starting game \'{game_ref}\' in channel {channel_id} [path: {game_data["path"]}, class: {game_data["class"]}]')

        # create the game instance
        self.games[channel_id] = DiscGameInstance(user_id, game_data, self.bot, text_channel)

        # register the game tick events
        self.events.on('second', self.games[channel_id].game._every_second_interal)
        self.events.on('minute', self.games[channel_id].game._every_minute_interal)

        # call game startup
        await self.games[channel_id].startup()



    # End existing game
    async def end_game(self, channel_id, user_id):

        # check for existing game
        if self.get_game(channel_id) is None:
            self.logger.debug(f'Ending game: no game to end')

        self.logger.info(f'Ending game \'{self.games[channel_id].ref}\' in channel {channel_id}')

        # deregister the game tick events
        self.events.off('second', self.games[channel_id].game._every_second_interal)
        self.events.off('minute', self.games[channel_id].game._every_minute_interal)

        await self.games[channel_id].shutdown()
        del self.games[channel_id]

        

    # Handle game message for existing game
    async def game_message(self, channel_id, user_id, msg):
        pass
    
    # Hibernate this launcher
    def hibernate(self):
        self.logger.info(f'Launcher [{self.name}] hibernating')

        self.events.off('minute', self._every_minute)
        self.events.off('second', self._every_second)

    # Wake up up this launcher
    def wake(self):
        self.logger.info(f'Launcher [{self.name}] waking up')

        self.loop = asyncio.create_task(self.update_loop())
        self.events.on('minute', self._every_minute)
        self.events.on('second', self._every_second)

        self.idle_time = -1
        self.restart_time = datetime.now()
        self.dead = False