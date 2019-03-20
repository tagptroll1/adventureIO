import logging
import os
from pathlib import Path

from .adventure_bot import AdventureBot
from .constants import Bot as BotConfig, IDS


OWNERS = (IDS.creator, IDS.benny)

log = logging.getLogger(__name__)
bot = AdventureBot(command_prefix=BotConfig.prefix)

@bot.group(name="git")
async def git_group(ctx):
    """Group for git commands"""

@git_group.command(name="pull")
async def git_pull_command(ctx):
    """Pulls any updates for the bot from git"""
    try:
        os.system("git pull origin master")
    except Exception as e:
        await ctx.send(f"```{e}```")

@bot.group(name="bot")
async def bot_group(ctx):
    """Group for bot commands"""

@bot_group.command(name="shutdown", aliases=("exit", "kill"))
async def bot_shutdown_command(ctx):
    if ctx.author.id not in OWNERS:
        return
    await bot.logout()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong <@234048816033038337>")

@bot_group.command()
async def reload_cogs(ctx):
    output = []
    for x in bot.cogs.values():
        output.append(x)

    await ctx.send("\n".join(output))

cogs = Path("./adventureIO/cogs")
print(cogs.absolute())
for cog in cogs.iterdir():
    if cog.is_dir():
        continue
    if cog.suffix == ".py":
        path = ".".join(cog.with_suffix("").parts)

        try:
            bot.load_extension(path)
            print(f"Loading... {path:<22} Success!")
            log.info(f"Loading... {path:<22} Success!")
        except Exception as e:
            log.exception(f"\nLoading... {path:<22} Failed!")
            print("-"*25)
            print(f"Loading... {path:<22} Failed!")
            print(e, "\n" , "-"*25, "\n")


bot.run(BotConfig.token)
