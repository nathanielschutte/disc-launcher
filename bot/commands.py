
# Discord Cog - handle commands

from discord.ext import commands

from bot.tools.util import path_resolve
from bot.tools import store
from .config import Config

class Games(commands.Cog):

    def __init__(self, bot, launcher) -> None:
        super().__init__()

        self.bot = bot

    @commands.command(help='')
    async def play(ctx, game):
        pass

