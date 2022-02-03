
# Run bot script

import os, sys

def main():
    print('hello')

verbose = '-v' in sys.argv

required_dirs = [
    'bot',
    'config'
]

def log(*msgs):
    if verbose:
        print(' '.join(msgs))

def check_env() -> None:
    log('Checking bot environment...')
    try:
        for dir in required_dirs:
            assert os.path.isdir(dir), f'directory not found: {dir}'
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
    log('Exited with code', main())
