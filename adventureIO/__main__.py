from adventure_bot import AdventureBot
from constants import bot as BotConfig

bot = AdventureBot(commands_prefix=BotConfig.prefix)
bot.run(BotConfig.token)