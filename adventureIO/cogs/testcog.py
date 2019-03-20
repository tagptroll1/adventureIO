from discord.ext.commands import Cog, command

class TestCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def test(self, ctx):
        await ctx.send("I still work!")


def setup(bot):
    bot.add_cog(TestCog(bot))