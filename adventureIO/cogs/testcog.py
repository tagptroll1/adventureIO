import discord
from discord.ext.commands import Cog, command


class TestCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def embed(self, ctx):
        e = discord.Embed()
        e.description = "**Stuff:** 12341\n**More:** hahaha \n\n💬"
        await ctx.send(embed=e)

    @command()
    async def embed2(self, ctx):
        e = discord.Embed()
        e.description = "**Stuff:** 12341\n**More:** hahaha"
        e.set_footer(text="💬")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(TestCog(bot))