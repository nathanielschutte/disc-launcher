
# Game launcher - handle games for a discord server

import logging, importlib

from .config import Config
from .exceptions import GameAlreadyRunningException, InvalidGameException

class DiscGameInstance:
    ''''''

    def __init__(self, host, data) -> None:
        
        self.host = host
        self.title = data['title']
        self.ref = data['ref']
        self.source = data['source']
        self.object = data['object']

        self.game = None


class DiscLauncher:
    
    def __init__(self) -> None:
        
        self.config = Config()
        self.logger = logging.getLogger(self.config.log_name)

        # Game data per channel
        self.games = {} # channel_id: DiscGame




    # ===========================================
    # Launcher attributes
    def get_all_games(self):
        return self.games


    def get_game(self, channel_id) -> DiscGameInstance:
        if channel_id in self.games:
            return self.games[channel_id]
        else:
            return None

    def library(self):
        return self.config.game_lib


    def valid_game_ref(self, game_ref):
        return game_ref in self.library()


    # ===========================================
    # Events from bot

    # Start a new game
    def start_game(self, channel_id, user_id, game_ref):

        # check for existing game
        if self.get_game(channel_id) is not None:
            raise GameAlreadyRunningException(f'Channel {channel_id} has a game already running')

        # check if the game exists in library
        if not self.valid_game_ref(game_ref):
            raise InvalidGameException(None)

        # set game data
        game_data = self.library()[game_ref]
        self.games[channel_id] = DiscGameInstance(user_id, game_data)

        self.logger.info(f'Starting game \'{game_ref}\' in channel {channel_id} [source: {game_data["source"]}, object: {game_data["object"]}]')

        

        #cls = getattr(import_module('my_module'), 'my_class')
    

    # End existing game
    def end_game(self, channel_id, user_id):

        # check for existing game
        if self.get_game(channel_id) is None:
            self.logger.debug(f'Ending game: no game to end')

        del self.games[channel_id]

        

    # Handle game message for existing game
    def game_message(self, channel_id, user_id, msg):
        pass
    