from discord.ext.commands import Bot
from constants import bot as BotConfig

bot = Bot(commands_prefix=BotConfig.prefix)
bot.run(BotConfig.token)