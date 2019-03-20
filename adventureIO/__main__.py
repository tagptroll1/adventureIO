import logging
import os

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
    
@bot_group.command(name="os")
async def bot_os_command(ctx, *, text):
    if ctx.author.id not in OWNERS:
        return
    os.system(text)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong <@234048816033038337>")


bot.run(BotConfig.token)
