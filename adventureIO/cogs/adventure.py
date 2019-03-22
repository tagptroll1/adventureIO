from discord.ext.commands import Cog, command, group

import adventureIO.database as database


class AdventureCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_adventures = {}

        #bot.loop.create_task(self.sync_adventures())

    async def sync_adventures(self):
        adventurers = await database.get_adventurers()

    @group(name="adventure")
    async def adventure_group(self, ctx, *, rest = None):
        
        await ctx.invoke(self.adventure_alt_1, rest=rest)

    @adventure_group.command(name="1")
    async def adventure_alt_1(self, ctx, *, rest = None):
        ...

def setup(bot):
    bot.add_cog(AdventureCog(bot))