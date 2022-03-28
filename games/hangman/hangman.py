
# Hangman

from discgame import DiscGame

# Implement the basic DiscGame object
class HangmanGame:

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
    
    def start(self):
        print(f'Hello from {self.__class__}')

        self.monitor

