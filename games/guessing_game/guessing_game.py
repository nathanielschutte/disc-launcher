
# Simple turn-based game implementation

# Load DiscGame from absolute path for now
# This should be done through pip eventually
import sys
sys.path.append('C:/Users/Nate/Documents/projects/repos/disc-launcher/bot')
from bot.game import DiscGame

# Implement the basic DiscGame object
class GuessingGame(DiscGame):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
    
    def start(self):
        print(f'Hello from {self.__class__}')
