
# Game launcher - handle games for a discord server

import logging

from .config import Config
from .exceptions import GameAlreadyRunningException, InvalidGameException

class DiscGameInstance:
    ''''''

    def __init__(self, title, admin, data) -> None:
        
        self.title
        self.admin = admin
        self.data = data

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


    def get_game(self, channel_id):
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

        self.logger.debug(f'Starting game \'{game_ref}\' in channel {channel_id} [source: {game_data["source"]}, object: {game_data["object"]}]')


        #cls = getattr(import_module('my_module'), 'my_class')