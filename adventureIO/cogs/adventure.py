from discord.ext.commands import Cog, command, group

from adventureIO import database
from ..adventure_files.adventure import Adventure
from ..adventure_files.player import Player


class AdventureCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_adventures = {}
        self.active_players = {}
        self.queue = []

        # bot.loop.create_task(self.async__init__())

    async def async__init__(self):
        ...
        # async for adventure in database.get_adventurers():
        #   player = self.bot.get_user(adventure["player_id"])
        #   type = adventure["type"]
        #   running = adventure["running"]
        #   enemy_tuple = await database.get_active_mob(adventure["enemy_id"])
        #   enemy_params = (
        #       "id", "name", "desc", "hp", "atk",
        #       "res", "crit", "loot", "max_hp",
        #   )
        #   enemy_dict = dict(zip(enemy_params, enemy_tuple))
        #   enemy = Enemy(**enemy_dict)
        #   instance = Battle(player, enemy)
        #   adventure = Adventure(player, type, running, instance)
        #   self.active_adventures[player.id] = adventure
        #   self.active_players[player.id] = player
        #   await self.update_player_queue(player.id)
        # print("Loaded", len(self.queue), "adventures")

    async def ensure_save(self, player_id):
        print("Totally saved", player_id)

    async def update_player_queue(self, player_id):
        if player_id in self.queue:
            index = self.queue.index(player_id)
            self.queue.append(self.queue.pop(index))
        else:
            self.queue.append(player_id)

        if len(self.queue) > 1000:
            await self.ensure_save(self.queue.pop())

    @group(name="adventure", aliases=("adv", "a"), invoke_without_command=True)
    async def adventure_group(self, ctx, *, rest=None):

        await ctx.invoke(self.adventure_alt_1, rest=rest)

    @adventure_group.command(name="1")
    async def adventure_alt_1(self, ctx, *, rest=None):
        author = ctx.author

        if author.id not in self.active_players:
            player = Player(author)
            if not player.activated:
                return await ctx.send(
                    "Please create an account before playing.\n"
                    f"You can do so with {ctx.prefix}create"
                )
            self.active_players[author.id] = player

        player = self.active_players[author.id]

        if author.id not in self.active_adventures:
            adventure = Adventure(player)
            self.active_adventures[author.id] = adventure

        adventure = self.active_adventures[author.id]

        await self.update_player_queue(author.id)

        if adventure.running:
            await adventure.continue_(ctx, rest)
        else:
            await adventure.start(ctx, rest)

    @adventure_group.command(name="2")
    async def adventure_alt_2(self, ctx, *, rest=None):
        author = ctx.author

        if author.id not in self.active_players:
            return
        if author.id not in self.active_adventures:
            return

        player = self.active_players[author.id]
        self.active_adventures[author.id] = Adventure(player)

        await ctx.send("You ran from your adventure!")

    @adventure_group.command(name="revive")
    async def adventure_revive(self, ctx):
        adventure = self.active_adventures.get(ctx.author.id)
        if adventure:
            adventure.revive()
            await ctx.send("Revived")
        else:
            await ctx.send("You don't even have an adventure going..")

    @command(name="create")
    async def create_player_command(self, ctx):
        package = {
            "playerid": ctx.author.id,
            "name": ctx.author.display_name,
        }

        player = await database.insert_player(self.bot.pool, package)

        if player:
            if not player["activated"]:
                return await ctx.send(
                    f"{ctx.author.mention} already have an account, "
                    "but is not activated!\n"
                    f"{ctx.prefix}activate to activate your account."
                )
            return await ctx.send(
                f"{ctx.author.mention} "
                "already have an account!"
            )

        await ctx.send(
            f"Created account, don't forget to activate it with "
            f"{ctx.prefix}activate!"
        )


def setup(bot):
    bot.add_cog(AdventureCog(bot))
