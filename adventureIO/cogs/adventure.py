from discord import Member
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

        bot.loop.create_task(self.async__init__())

    async def async__init__(self):
        ...

    async def ensure_save(self, player_id):
        adventure = self.active_adventures.get(player_id)
        # if adventure:
        #   await self.bot.db.update_adventure()
        player = self.active_players.get(player_id)
        if player:
            await self.bot.db.update_player(player)
            
        print("Totally saved", player_id)

    async def update_player_queue(self, player_id):
        if player_id in self.queue:
            index = self.queue.index(player_id)
            self.queue.append(self.queue.pop(index))
        else:
            self.queue.append(player_id)

        if len(self.queue) > 1000:
            to_del = self.queue.pop()
            await self.ensure_save(to_del)

            try:
                del self.active_adventures[to_del]
            except IndexError:
                print(
                    "Tried to delete from adeventures "
                    "on queue update above 1000 entries"
                )

            try:
                del self.active_players[to_del]
            except IndexError:
                print(
                    "Tried to delete from players "
                    "on queue update above 1000 entries"
                )

    @group(name="adventure", aliases=("adv", "a"), invoke_without_command=True)
    async def adventure_group(self, ctx, *, rest=None):

        await ctx.invoke(self.adventure_alt_1, rest=rest)

    @adventure_group.command(name="1")
    async def adventure_alt_1(self, ctx, *, rest=None):
        author = ctx.author

        if author.id not in self.active_players:
            player_row = await self.bot.db.fetch_player(author.id)

            if player_row:
                player = Player.from_database(author, player_row)
            else:
                player = Player(author)

            if not player.activated:
                return await ctx.send(
                    "Please create an account before playing.\n"
                    f"You can do so with {ctx.prefix}create"
                )
            self.active_players[author.id] = player

        player = self.active_players[author.id]

        if player.dead:
            return await ctx.send("You're dead, silly!")

        if author.id not in self.active_adventures:
            adventure = Adventure(player)
            self.active_adventures[author.id] = adventure

        adventure = self.active_adventures[author.id]

        await self.update_player_queue(author.id)

        if adventure.running:
            await adventure.continue_(ctx, rest)
        else:
            await adventure.start(ctx, rest)

        await self.bot.db.update_player(player)

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
            if not adventure.revive():
                await ctx.send("Revived")
            else:
                await ctx.send("You're not dead...")
        else:
            player = self.active_players.get(ctx.author.id)

            if not player:
                player = self.bot.db.fetch_player(ctx.author.id)

            if not player:
                return await ctx.send("Create an account first!")

            if not player.activated:
                return await ctx.send("Activate your account first!")

            if player.hp > 0:
                return await ctx.send("You're not even dead...")

            player.revive()
            await ctx.send("Revived")
            await self.bot.db.update_player(player)
        

    @command(name="create")
    async def create_player_command(self, ctx):
        if ctx.author.id in self.active_players:
            player = self.active_players.get(ctx.author.id)
        else:
            package = {
                "playerid": ctx.author.id,
                "name": ctx.author.display_name,
            }

            await self.bot.db.insert_player(package)

            player_row = await self.bot.db.fetch_player(ctx.author.id)

            player = Player.from_database(ctx.author, player_row)

        if player and not player.activated:
            return await ctx.send(
                f"{ctx.author.mention} already have an account, "
                "but is not activated!\n"
                f"{ctx.prefix}activate to activate your account."
            )
        elif player:
            return await ctx.send(
                f"{ctx.author.mention} "
                "already have an account!"
            )
        else:
            await ctx.send(
                f"Created account, don't forget to activate it with "
                f"{ctx.prefix}activate!"
            )

    @command(name="activate")
    async def activate_player_command(self, ctx, member: Member = None):
        if not member:
            member = ctx.author

        if member.id not in self.active_players:
            player_row = await self.bot.db.fetch_player(member.id)

            if not player_row:
                return await ctx.send(
                    "No account found, "
                    f"please create one with {ctx.prefix}create"
                )

            print(player_row)
            player = Player.from_database(member, player_row)
        else:
            player = self.active_players.get(member.id)

        if player and player.activated:
            return await ctx.send("Your account is already activated.")

        if not player:
            await ctx.send("wtf, couldnt find you?")

        await player.activate(ctx)
        self.active_players[member.id] = player


def setup(bot):
    bot.add_cog(AdventureCog(bot))
