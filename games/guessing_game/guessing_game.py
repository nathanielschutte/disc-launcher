
# Simple turn-based game implementation

from datetime import datetime

from discgame import DiscGame

# Implement the basic DiscGame object
class GuessingGame(DiscGame):

    def __init__(self, monitor):
        super().__init__(monitor)
    
    async def start(self):
        pass

    async def end(self):
        await self.monitor.send_endcard('Results')
    
    async def join(self):
        pass

    async def leave(self):
        pass

    async def message(self):
        pass

    async def every_second(self):
        await self.monitor.send(f'I have been alive for {(datetime.now() - self.started_at).total_seconds():.1f} seconds!')

    async def every_minute(self):
        pass
    