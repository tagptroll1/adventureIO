from discord.ext.commands import Cog, command, group

import adventureIO.database as database


class AdventureDevelopmentCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(name="dev")
    async def developer_group(self, ctx):
        ...

    @developer_group.group(name="add")
    async def developer_add_group(self, ctx):
        ...

    @developer_add_group.command(name="item")
    async def add_item_to_database(self, ctx, name):
        item = await database.check_item_exists(name)
        if item:
            return await ctx.send(f"This item already exists: {item}")


        add_item_keys = ["price", "weight", "rarity", "use1", "use2"]
        kwargs = {"name": name}

        for key in add_item_keys:
            await ctx.send(f"{key}? 'no' to leave it blank")
            msg = await self.bot.wait_for(
                "message", 
                check=lambda msg: msg.author.id == ctx.author.id
            )

            if msg.content.lower() == "no":
                kwargs[key] = None
            else:
                kwargs[key] = msg.content

        await database.add_item(**kwargs)


def setup(bot):
    bot.add_cog(AdventureDevelopmentCog(bot))