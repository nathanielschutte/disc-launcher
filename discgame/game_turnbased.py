
from .game import DiscGame

# Turn-based game
class DiscTurnBasedGame(DiscGame):
    def __init__(self) -> None:
        super().__init__()
