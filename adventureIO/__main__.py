import asyncio
import logging

from adventureIO.adventure_bot import AdventureBot
from adventureIO.constants import Bot as BotConfig
from adventureIO import database


log = logging.getLogger(__name__)


async def start_bot():
    pool = await database.get_pool()
    bot = AdventureBot(pool=pool, command_prefix=BotConfig.prefix)
    await database.setup_tables(bot)
    await bot.start(BotConfig.token)


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
except Exception as e:
    log.warning("Exception raised from main thread.")
    log.exception(e)
