import logging
import os

from adventureIO.adventure_bot import AdventureBot
from adventureIO.constants import Bot as BotConfig, IDS


OWNERS = (*IDS.creators, IDS.benny)

log = logging.getLogger(__name__)
bot = AdventureBot(command_prefix=BotConfig.prefix)


@bot.group(name="git")
async def git_group(ctx):
    """Group for git commands"""


@git_group.command(name="pull")
async def git_pull_command(ctx):
    """Pulls any updates for the bot from git"""
    try:
        os.system("git pull origin master > gitoutput.txt")
        with open("gitoutput.txt") as f:
            await ctx.send(f.read())
        os.remove("gitoutput.txt")
    except Exception as e:
        await ctx.send(f"```{e}```")


@bot.group(name="bot")
async def bot_group(ctx):
    """Group for bot commands"""


@bot_group.command(name="shutdown", aliases=("exit", "kill"))
async def bot_shutdown_command(ctx):
    """Logs the bot out, this kills the process"""
    
    if ctx.author.id not in OWNERS:
        return
    await bot.logout()


@bot.command()
async def ping(ctx):
    """Pong"""

    await ctx.send("Pong <@234048816033038337>")


@bot_group.command()
async def reload_cogs(ctx):
    """
    Utility command to reload every cog the bot has loaded.

    This recreates all the class instances of the cogs,
    which in turn call the __init__ again for all of them.
    """

    if ctx.author.id not in OWNERS:
        return
    temp = []
    errors = []

    for x in bot.extensions:
        temp.append(x)
        try:
            bot.unload_extension(x)
            bot.load_extension(x)
        except Exception as e:
            errors.append(str(e))

    await ctx.send("Done!")
    if errors:
        error = "\n".join(errors)
        await ctx.send(f"```{error}```")


@bot_group.command(name="reload")
async def reload_cog(ctx, *, cog):
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
        bot.unload_extension(cog)
        bot.load_extension(cog)
    except Exception as e:
        return await ctx.send(f"```{e}```")

    await ctx.send("Done")


bot.run(BotConfig.token)
