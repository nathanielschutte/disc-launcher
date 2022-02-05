
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

        self.commands = {} # command: [aliases, desc, usage]
        self.whitelist = [] # [servers]

        # Propogate load errors
        try:
            # Load config
            self.__load_config()

            # Load command aliases and help
            self.__load_commands()

            # Load server whitelist
            self.__load_whitelist()

            # Load game library
            self.__load_games()

        except ConfigLoadError as e:
            raise ConfigLoadError(str(e))
        except Exception as e:
            raise ConfigLoadError(f'uncaught {type(e)}: {str(e)}')


    def __load_config(self):

        config = configparser.ConfigParser()
        config.read(self.file)

        # Check required sections...

        # Bot config
        self.bot_prefix = config.get('bot', 'prefix', fallback='!')
        self.bot_title = config.get('bot', 'title', fallback='Games')
        self.bot_name = config.get('bot', 'name', fallback='Games')
        self.bot_activity = config.get('bot', 'activity', fallback='')

        # Command aliases config
        self.use_aliases = config.getint('bot', 'aliases_disable', fallback=0) == 0
        self.commands_file = path_resolve(config.get('bot', 'commands_file', fallback='config/bot/aliases.json'), force_exists=False)

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
        self.stdout = config.getint('logging', 'stdout_disable', fallback=1) == 0

    
    def __load_commands(self):
        
        if not os.path.isfile(self.commands_file):
            raise ConfigLoadError(f'Commands error: no file \'{self.commands_file}\'')

        with open(self.commands_file, 'r') as file:
            content = file.read()
            try:
                commands = json.loads(content)
            except json.JSONDecodeError:
                raise ConfigLoadError(f'Commands file error: could not parse \'{self.commands_file}\'')
            for command, info in commands.items():
                if command not in self.commands:
                    self.commands[command] = {
                        'aliases': [],
                        'desc': '',
                        'usage': ''
                    }
                if 'aliases' in info and isinstance(info['aliases'], list):
                    self.commands[command]['aliases'] = info['aliases']
                if 'desc' in info:
                    self.commands[command]['desc'] = info['desc']
                if 'usage' in info:
                    self.commands[command]['usage'] = info['usage']


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

