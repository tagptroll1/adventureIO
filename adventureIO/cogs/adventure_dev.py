from discord.ext.commands import Cog, group

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

    @developer_group.group(name="remove", aliases=["delete"])
    async def developer_remove_group(self, ctx):
        ...

    @developer_add_group.command(name="item")
    async def add_item_to_database(self, ctx, *, name):
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

    @developer_remove_group.command(name="item")
    async def remove_item_command(self, ctx, *, item):
        try:
            item = int(item)
            _int = True
        except ValueError:
            _int = False

        if _int:
            await database.delete_by_id(item, 'items')
        else:
            await database.delete_by_name(item, 'items')

        await ctx.send("Done")

    @developer_group.command(name="get")
    async def developer_get_group(self, ctx):
        all_items = [
            (
                f"{'Id':^4}|{'Name':^26}|{'Price':^7}|"
                f"{'Weight':^8}|{'Rarirty':^9}|{'Use1':^6}|"
                f"{'Use2':^6}|{'Purchaseable':^14}"
            ),
            (
                f"{'-'*4}+{'-'*26}+{'-'*7}+{'-'*8}+"
                f"{'-'*9}+{'-'*6}+{'-'*6}+{'-'*14}"
            )
        ]
        async for item in database.AllItems():
            _id, name, price, weight, rarity, use1, use2, shop = item
            _id = str(_id)
            price = str(price)
            weight = str(weight)
            rarity = str(rarity)
            use1 = str(use1)
            use2 = str(use2)

            _str = (
                f"{_id[:4]:^4}|{name[:26]:^26}|{price[:7]:^7}|"
                f"{weight[:8]:^8}|{rarity[:9]:^9}|{use1[:6]:^6}|"
                f"{use2[:6]:^6}|{'True' if shop else 'False':^14}"
            )
            all_items.append(_str)
        await ctx.send("```css\n{}```".format("\n".join(all_items)))


def setup(bot):
    bot.add_cog(AdventureDevelopmentCog(bot))
