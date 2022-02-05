
# Utility functions

import os, logging

class Singleton(type):
    '''Use as metaclass to implement singleton pattern'''

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def path_resolve(filename, force_exists=True):
    '''If filename is not found, check if it exists relative to project root'''

    if os.path.exists(filename):
        return filename

    rootpath = os.path.normpath(os.path.dirname(os.path.realpath(__file__))).split(os.sep)
    fullpath = os.path.join(f'{os.sep}'.join(rootpath[:rootpath.index('bot')]), filename)

    if not force_exists or os.path.exists(fullpath):
        return fullpath
    else:
        raise IOError('Could not find: {}'.format(fullpath))
