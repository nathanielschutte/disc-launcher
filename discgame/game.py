
# Game objects

from datetime import datetime

from .constants import GameDefaults
from .monitor import DiscGameMonitor

# Base game
class DiscGame:
    def __init__(self, monitor) -> None:
        self.monitor = monitor

        self.started_at = datetime.now()        # datetime that this game was started
        self.ended_at = None                      # datetime that this game was ended
        self.last_message_time = None             # last time a message was received
        self.idle_time_seconds = datetime.now() # total idle time in seconds
        self.total_time_seconds = 0            # total runtime in seconds
        
        self.idle_timeout = GameDefaults.idle_timeout       

    def __str__(self) -> str:
        return 


    # ========================================
    # Interface calls
    async def start(self):
        pass

    async def stop(self):
        pass

    async def join(self):
        pass

    async def leave(self):
        pass

    async def message(self):
        pass

    async def every_second(self):
        pass

    async def every_minute(self):
        pass


    # ========================================
    # Interal calls
    async def _start_interal(self):
        self.started_at = datetime.now()

        await self.start()

    async def _end_internal(self):
        self.ended_at = datetime.now()

        await self.end()

    async def _join_internal(self):
        
        await self.join()

    async def _message_interal(self):
        self.last_message_time = datetime.now()

        await self.message()

    async def _every_second_interal(self):
        
        if self.last_message_time is None:
            self.idle_time_seconds = (datetime.now() - self.started_at).total_seconds()
        else:
            self.idle_time_seconds = (datetime.now() - self.last_message_time).total_seconds()
            
        self.total_time_seconds = (datetime.now() - self.started_at).total_seconds()

        await self.every_second()
    
    async def _every_minute_interal(self):
        
        # checks

        await self.every_minute()

