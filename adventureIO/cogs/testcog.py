from discord.ext.commands import Cog, command

class TestCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def test(self, ctx):
        await ctx.send("I still still still still work!")


    @command()
    async def newstuff(self, ctx):
        await ctx.send("this is super new")

    @command()
    async def thisthing(self, ctx):
        await ctx.send("hello me tho you")

def setup(bot):
    bot.add_cog(TestCog(bot))