import os

from discord.ext.commands import Cog, command, group
from adventureIO.constants import IDS, Originator

OWNERS = (*IDS.creators, IDS.benny)


class BotCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(name="git")
    async def git_group(self, ctx):
        """Group for git commands"""

    @git_group.command(name="pull")
    async def git_pull_command(self, ctx):
        """Pulls any updates for the bot from git"""
        try:
            os.system("git pull origin master > gitoutput.txt")
            with open("gitoutput.txt") as f:
                await ctx.send(f.read())
            os.remove("gitoutput.txt")
        except Exception as e:
            await ctx.send(f"```{e}```")

    @group(name="bot")
    async def group_bot(self, ctx):
        """Group for bot commands"""

    @group_bot.command(name="shutdown", aliases=("exit", "kill"))
    async def shutdown_command(self, ctx):
        """Logs the bot out, this kills the process"""

        if ctx.author.id not in OWNERS:
            return
        await ctx.send("shutting down...")
        await self.bot.logout()

    @command()
    async def ping(self, ctx):
        """Pong"""

        await ctx.send("Pong <@234048816033038337>")

    @group_bot.command(name="originator")
    async def originator(ctx):
        await ctx.send(Originator.name)

    @group_bot.command()
    async def reload_cogs(self, ctx):
        """
        Utility command to reload every cog the bot has loaded.

        This recreates all the class instances of the cogs,
        which in turn call the __init__ again for all of them.
        """

        if ctx.author.id not in OWNERS:
            return
        temp = []
        errors = []

        for x in self.bot.extensions:
            temp.append(x)
            try:
                self.bot.unload_extension(x)
                self.bot.load_extension(x)
            except Exception as e:
                errors.append(str(e))

        await ctx.send("Done!")
        if errors:
            error = "\n".join(errors)
            await ctx.send(f"```{error}```")

    @group_bot.command(name="reload")
    async def reload_cog(self, ctx, *, cog):
        """
        Utility command to unload and load a cog.

        This recreates the class instance and reloads the __init__ call
        :param cog: Name of the cog to be reloaded.
        """

        if not cog.count(".") == 2:
            if cog.startswith("cogs."):
                cog = f"adventureIO.{cog}"
            else:
                cog = f"adventureIO.cogs.{cog}"

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            return await ctx.send(f"```{e}```")

        await ctx.send("Done")


def setup(bot):
    bot.add_cog(BotCog(bot))
