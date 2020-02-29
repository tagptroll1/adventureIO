import asyncio
import logging

import asyncpg

from adventureIO.adventure_bot import AdventureBot
from adventureIO.constants import Bot as BotConfig, Database
from adventureIO import database


log = logging.getLogger(__name__)


async def start_bot():
    pool = await asyncpg.create_pool(
        Database.url,
        min_size=3,
        max_size=3
    )
    database_instance = database.Database(pool)
    bot = AdventureBot(database_instance, command_prefix=BotConfig.prefix)
    await bot.db.setup_tables()
    await bot.start(BotConfig.token)


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
except Exception as e:
    log.warning("Exception raised from main thread.")
    log.exception(e)
