
# Monitor for a DiscGame with functions to update it

import logging, asyncio

from .constants import GameDefaults
from discord import NotFound

class DiscGameMonitor:

    def __init__(self, bot, text_channel) -> None:
        self.tc = text_channel
        self.bot = bot
        self.message = None

        self.screen: DiscGameScreen = DiscGameScreen(GameDefaults.screen_size)
        self.action = ''
        self.content = ''
        self.footer = ''

        self.lock = asyncio.Lock()

    async def send(self, content):
        await self.__send(content=content)

    async def send_game(self):
        await self.__send(content=f'```{str(self.screen)}```')

    async def send_note(self, note):
        await self.__send(content=note)
    
    async def send_endcard(self, content):
        await self.__send(content=content, nodelete=True)

    async def __update_message(self):
        async with self.lock: 
            msg = None
            if self.message is None:
                msg = await self.tc.send('Generating...')
            else:
                async for _msg in self.tc.history(limit=1):
                    if _msg.id != self.message.id:
                        try:
                            await self.message.delete()
                        except NotFound:
                            pass
                        msg = await self.tc.send('Generating...')
                    else:
                        msg = _msg

            if msg is not None:
                self.message = msg
                return True
            else:
                print('error updating the monitor message')
                return False

    async def __send(self, nodelete=False, **kwargs):
        if nodelete:
            await self.tc.send(**kwargs)
        elif await self.__update_message():
            async with self.lock:
                # chance that clean got here first
                try:
                    await self.message.edit(**kwargs)
                except NotFound:
                    pass
        else:
            print('error sending monitor')

    async def clean(self):
        async with self.lock:
            if self.message is not None:
                try:
                    await self.message.delete()
                except NotFound:
                    pass
        
class DiscGameScreen:

    def __init__(self, size) -> None:
        self.size = size

        self.__set_matrix()

    def __str__(self) -> str:
        return '\n'.join([''.join(self.matrix[i]) for i in range(self.size)])

    def __set_matrix(self, size=-1):
        if size == -1:
            size = self.size
        self.matrix = [['.' for _ in range(self.size)] for _ in range(self.size)]
