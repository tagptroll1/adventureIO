from discord.ext.commands import Bot, command, group, is_owner

class AdventureBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_message(self, message):
        print(message.content)

        await self.process_commands(message)
