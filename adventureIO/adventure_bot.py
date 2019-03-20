from discord.ext.commands import Bot, command, group, is_owner
from .constants import IDS

OWNERS = (IDS.creator, IDS.benny)

class AdventureBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_message(self, message):
        print(message.content)

        await self.process_commands(message)
