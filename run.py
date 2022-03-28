
# Run bot script

import os, sys

# affects run script output only
verbose = '-v' in sys.argv

required_dirs = [
    'bot',
    'config/bot',
    'discgame'
]

def log(*msgs):
    if verbose:
        print(' '.join(msgs))

def check_env() -> None:
    log('Checking bot environment...')
    from bot.tools.util import path_resolve
    try:
        for dir in required_dirs:
            log(f'Checking {path_resolve(dir)}...')
            assert os.path.isdir(path_resolve(dir)), f'directory not found: {dir}'
    except AssertionError as e:
        log(f'Environment error: {e}')
        exit(1)

    log('Environment OK')

def main() -> int:

    check_env()

    from bot.runner import Runner
    runner = Runner()
    return runner.run()

if __name__ == '__main__':
    log('Exited with code', str(main()))
