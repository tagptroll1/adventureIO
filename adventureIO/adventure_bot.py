import os

from discord.ext.commands import Bot, command, group, is_owner


OWNERS = (IDS.creator, IDS.benny)

class AdventureBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_message(self, message):
        print(message.content)

        await self.process_commands(message)

    @group(name="git")
    async def git_group(self, ctx):
        """Group for git commands"""

    @git_group.command(name="pull")
    async def git_pull_command(self, ctx):
        """Pulls any updates for the bot from git"""
        try:
            os.system("git pull origin master")
        except Exception as e:
            await ctx.send(f"```{e}```")

    @group(name="bot")
    async def bot_group(self, ctx):
        """Group for bot commands"""

    @bot_group.commands(name="shutdown", aliases=("exit", "kill"))
    async def bot_shutdown_command(self, ctx):
        if ctx.author.id not in OWNERS:
            return
        await self.logout()