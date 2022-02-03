
# Store config values

import os, shutil
import configparser

from bot.exceptions import FormattedException
from bot.tools.util import path_resolve, Singleton


class Config(metaclass=Singleton):

    def __init__(self, file=None) -> None:
        
        if file is None:
            file = 'config/bot/config.ini'

        self.file = path_resolve(file)

        if not os.path.isfile(self.file):
            if os.path.isfile(self.file + '.ini'):
                self.file += '.ini'
            elif os.path.isfile('config/config_template.ini'):
                shutil.copy('config/config_template.ini', self.file)
            else:
                raise FormattedException(f'Config file not found: {self.file}')

        config = configparser.ConfigParser()
        config.read(self.file)

        # Check required sections...

        # Bot config
        self.use_aliases = config.getint('bot', 'aliases_disable', fallback=0) == 0
        self.alias_file = path_resolve(config.get('bot', 'aliase_file', fallback='config/bot/aliases.json'), force_exists=False)
        self.bot_prefix = config.get('bot', 'prefix', fallback='!')

        # Logging config
        self.log_level = config.getint('logging', 'level', fallback=20)
        self.log_file = config.get('logging', 'file', fallback='out.log')
        self.log_name = config.get('logging', 'name', fallback='bot')
        self.log_showname = config.getint('logging', 'name_disable', fallback=0) == 0

        # Command help
        self.help = {}
        if config.has_section('help'):
            for opt in config.options('help'):
                self.help[opt] = config.get('help', opt, fallback='')
