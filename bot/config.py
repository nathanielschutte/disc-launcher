
# Store config values

import os, shutil, logging, json
import configparser

from bot.exceptions import ConfigLoadError, GameLoadError
from bot.tools.util import path_resolve, Singleton

# Log level translation
LOG_LEVEL = {
    'none': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Required fields for game library entries
GAME_REQ = {'source', 'object', 'title'}

# Config data
class Config(metaclass=Singleton):

    def __init__(self, file=None) -> None:
        
        # Look for config file
        if file is None:
            file = 'config/bot/config.ini'

        self.file = path_resolve(file)

        # Try to copy from template if not found
        if not os.path.isfile(self.file):
            if os.path.isfile(self.file + '.ini'):
                self.file += '.ini'
            elif os.path.isfile('config/config_template.ini'):
                shutil.copy('config/config_template.ini', self.file)
            else:
                raise ConfigLoadError(f'Config file not found: {self.file}')

        self.aliases = {} # command: [aliases]
        self.whitelist = [] # [servers]

        # Propogate load errors
        try:
            # Load config
            self.__load_config()

            # Load aliases
            self.__load_aliases()

            # Load server whitelist
            self.__load_whitelist()

            # Load game library
            self.__load_games()

        except ConfigLoadError as e:
            raise ConfigLoadError(str(e))
        except Exception as e:
            raise ConfigLoadError(f'uncaught: {str(e)}')


    def __load_config(self):

        config = configparser.ConfigParser()
        config.read(self.file)

        # Check required sections...

        # Bot config
        self.bot_prefix = config.get('bot', 'prefix', fallback='!')

        # Command aliases config
        self.use_aliases = config.getint('bot', 'aliases_disable', fallback=0) == 0
        self.alias_file = path_resolve(config.get('bot', 'aliase_file', fallback='config/bot/aliases.json'), force_exists=False)

        # Server whitelist config
        self.use_whitelist = config.getint('bot', 'whitelist_disable', fallback=0) == 0
        self.whitelist_file = path_resolve(config.get('bot', 'whitelist_file', fallback='config/bot/whitelist'), force_exists=False)

        # Launcher config
        self.game_file = path_resolve(config.get('launcher', 'game_file', fallback='config/launcher/games.json'), force_exists=False)

        # Logging config
        temp_level = config.get('logging', 'level', fallback='info').lower()
        self.log_level = LOG_LEVEL[temp_level] if temp_level in LOG_LEVEL else logging.INFO
        self.log_file = config.get('logging', 'file', fallback='out.log')
        self.log_name = config.get('logging', 'name', fallback='bot')
        self.log_showname = config.getint('logging', 'name_disable', fallback=0) == 0

        # Command help
        self.help = {}
        if config.has_section('help'):
            for opt in config.options('help'):
                self.help[opt] = config.get('help', opt, fallback='')

    
    def __load_aliases(self):
        pass

    def __load_whitelist(self):

        if not os.path.isfile(self.whitelist_file):
            raise ConfigLoadError(f'Whitelist error: no file \'{self.whitelist_file}\'')

        with open(self.whitelist_file, 'r') as file:
            for server in file.readlines():
                self.whitelist.append(server.strip())

    def __load_games(self):

        if not os.path.isfile(self.game_file):
            raise ConfigLoadError(f'Game library error: no file \'{self.game_file}\'')

        with open(self.game_file, 'r') as file:
            content = file.read()
            try:
                game_lib = json.loads(content)
            except json.JSONDecodeError:
                raise ConfigLoadError(f'Game library error: could not parse \'{self.game_file}\'')

            # create game library struct
            if 'games' in game_lib and isinstance(game_lib['games'], list):
                    self.game_lib = {}
                    for entry in game_lib['games']:
                        
                        diff = GAME_REQ.difference(set(entry.keys()))
                        if len(diff) > 0:
                            raise GameLoadError(f'Game library entry missing required fields: {diff}')

                        # index by ref priority
                        if 'ref' in entry:
                            self.game_lib[entry['ref']] = entry
                        
                        # or the full title
                        elif 'title' in entry:
                            self.game_lib[entry['title']] = entry
                        
                        # otherwise this entry is invalid
            else:
                self.game_lib = {}

