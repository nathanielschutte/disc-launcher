
# Store config values

import os, sys, shutil, logging, json, importlib
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
LIB_REQ = {'path'}
GAME_REQ = {'path', 'class', 'ref'}

# Config data
class Config(metaclass=Singleton):

    def __init__(self, file=None) -> None:
        self.load(file=file)

    def load(self, file=None) -> None:

        # Look for config file
        if file is None:
            file = 'config/bot/config.ini'

        self.file = path_resolve(file)

        # guaranteed to exist, need this for references to the DiscGame lib
        sys.path.append(path_resolve('discgame'))

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
        self.game_lib_config = {} # config game lib metadata
        self.game_lib = {} # game library

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
            raise ConfigLoadError(f'ConfigLoadError: {str(e)}')
        except GameLoadError as e:
            raise ConfigLoadError(f'GameLoadError: {str(e)}')
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

        # Launcher params
        self.launcher_idle_timeout = config.getint('bot', 'idle_timeout', fallback=60)

        # Game config

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

                # Skip disabled commands
                if 'disabled' in info and (info['disabled'] is True or info['disabled'] == 1):
                    if command in self.commands:
                        del self.commands[command]
                    continue

                # Add a new command entry
                if command not in self.commands:
                    self.commands[command] = {
                        'aliases': [],
                        'desc': '',
                        'usage': '',
                        'permission': 'any'
                    }

                # Populate command entry
                if 'aliases' in info and isinstance(info['aliases'], list):
                    self.commands[command]['aliases'] = info['aliases']
                if 'desc' in info:
                    self.commands[command]['desc'] = info['desc']
                if 'usage' in info:
                    self.commands[command]['usage'] = info['usage']
                if 'permission' in info:
                    self.commands[command]['permission'] = info['permission']


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

            # get library config
            if 'library' in game_lib and isinstance(game_lib['library'], dict):
                self.game_lib_config = {}

                # check required 'library' fields
                diff = LIB_REQ.difference(set(game_lib['library'].keys()))
                if len(diff) > 0:
                    raise GameLoadError(f'Game library info missing required fields: {diff}')
                
                # make sure path exists
                if not os.path.isdir(game_lib['library']['path']):
                    raise GameLoadError(f'Game library path not found: {game_lib["library"]["path"]}')

                # guaranteed fields
                self.game_lib_config['path'] = game_lib['library']['path']

                # add game library to path
                sys.path.append(self.game_lib_config['path'])

            else:
                raise ConfigLoadError(f'Game library error: no library info in \'{self.game_file}\'')


            # create game library struct
            if 'games' in game_lib and isinstance(game_lib['games'], list):
                    for entry in game_lib['games']:

                        # check required 'game' entry fields    
                        diff = GAME_REQ.difference(set(entry.keys()))
                        if len(diff) > 0:
                            raise GameLoadError(f'Game library entry missing required fields: {diff}')


                        # check that the game's path exists
                        if not os.path.isdir(os.path.join(self.game_lib_config['path'], entry['path'])):
                            raise GameLoadError(f'Game ({entry["ref"]}) path not found: {entry["path"]}')


                        # check for the game's object file
                        object_file = entry['class'].strip().split('.')[0]
                        object_class = entry['class'].strip().split('.')[1]

                        if not os.path.isfile(f'{os.path.join(self.game_lib_config["path"], entry["path"], object_file)}.py'):
                            raise GameLoadError(f'Game ({entry["ref"]}) object file not found: {object_file}')


                        # attempt to load the game path and object
                        module = None
                        try:
                            module = importlib.import_module(f'{entry["path"]}.{object_file}')
                        except Exception as e:
                            raise GameLoadError(f'Game ({entry["ref"]}) module could not be loaded: {str(e)}')
                        
                        # grab the entry DiscGame object
                        cls = None
                        if hasattr(module, object_class):
                            cls = getattr(module, object_class)
                        else:
                            raise GameLoadError(f'Game ({entry["ref"]}) object could not be found: {object_class}')


                        # add game to library
                        if cls is not None:
                            self.game_lib[entry['ref']] = entry
                            self.game_lib[entry['ref']]['object'] = cls
                        else:
                            raise GameLoadError(f'Game ({entry["ref"]}) object could not be loaded: {object_class}')


                        #print(f'loaded game {self.game_lib[entry["ref"]]["object"].__name__}')

            else:
                self.game_lib = {}

