import asyncio

import discord
from adventureIO.constants import Emoji


class PlayerNotActivatedError(Exception):
    ...


class Player:
    def __init__(self, member):
        self.member = member
        self.id = member.id
        self.name = member.name
        self.display_name = member.display_name
        self.activated = False

    @classmethod
    def from_database(cls, member, row):
        (
            _, _, hp, max_hp,
            atk, res, crit, luck,
            skillpoints, level, xp,
            money, activ, adventure_id
        ) = row

        player = cls(member)
        player.health = hp
        player.max_health = max_hp
        player.attack = atk
        player.resistance = res
        player.crit = crit
        player.luck = luck
        player.skillpoints = skillpoints
        player.level = level
        player.xp = xp
        player.money = money
        player.activated = activ
        player.adventure_id = adventure_id
        return player

    def __getattribute__(self, name):
        activated_attributes = (
            "attack", "atk",
            "resistance", "res",
            "health", "hp",
            "max_health", "max_hp",
            "crit",
        )

        activated = object.__getattribute__(self, "activated")

        if name in activated_attributes:
            if activated:
                return object.__getattribute__(self, name)

            error = f"Can't fetch {name} value from an unactivated player"
            raise PlayerNotActivatedError(error)

        return object.__getattribute__(self, name)

    @property
    def row(self):
        return (
            self.id,
            self.health,
            self.max_health,
            self.attack,
            self.resistance,
            self.crit,
            self.luck,
            self.skillpoints,
            self.level,
            self.xp,
            self.money,
            self.activated,
            self.adventure_id
        )

    @property
    def hp(self):
        return self.health

    @property
    def max_hp(self):
        return self.max_health

    @property
    def atk(self):
        return self.attack

    @property
    def res(self):
        return self.resistance

    async def activate(self, ctx):
        if self.activated:
            return await ctx.send("You're already activated!")

        self.activated = True

        # TODO: Start session to add skillpoints to player
        embed = self.freeskillpoints_embed()
        msg = await ctx.send(embed=embed)

        reactions = (Emoji._1, Emoji._2, Emoji._3, Emoji._4, Emoji._5)

        ctx.bot.loop.create_task(
            self.add_skillpoints_loop(ctx.bot, msg, reactions)
        )
        for reaction in reactions:
            await msg.add_reaction(reaction)

        return
        await ctx.send("Activated!")

    async def add_skillpoints_loop(self, bot, msg, emojis):
        def check(r, u):
            if u.bot:
                return False
            if r.message.id != msg.id:
                return False
            if r.emoji not in emojis:
                return False
            return True

        while self.skillpoints > 0:
            try:
                reaction, member = await bot.wait_for(
                    "reaction_add",
                    check=check,
                    timeout=60
                )
            except asyncio.TimeoutError:
                return False

            if reaction.emoji == Emoji._1:
                self.max_health += 5
                self.health = self.max_health
            elif reaction.emoji == Emoji._2:
                self.attack += 1
            elif reaction.emoji == Emoji._3:
                self.resistance += 1
            elif reaction.emoji == Emoji._4:
                self.crit += 1
            elif reaction.emoji == Emoji._5:
                self.luck += 1
            else:
                print("Unknown emoji? ", reaction.emoji)
                continue

            if self.skillpoints > 0:  # Probably redundant
                self.skillpoints -= 1

            embed = self.freeskillpoints_embed()
            await msg.edit(embed=embed)
            await msg.remove_reaction(reaction, member)

        try:
            await msg.clear_reactions()
            await msg.add_reaction(Emoji.checkmark)
        except discord.Forbidden:
            print("Missing permissions to clear reactions")

        if bot.db:
            await bot.db.update_player(self)

    def revive(self):
        self.health = self.max_health

    def freeskillpoints_embed(self):
        embed = discord.Embed(
            title=f"Add skillpoints ({self.skillpoints} left)"
            )

        longest = max(
            [
                len(str(num))
                for num
                in (self.max_hp, self.attack, self.res, self.crit, self.luck)
            ]
        )

        embed.description = (
            "*Use the number reactions to add points*\n\n"
            "```"
            f"1. {'Health:':<12}  [{self.max_hp:>{longest}}] ⁺⁵ \n"
            f"2. {'Attack:':<12}  [{self.attack:>{longest}}] ⁺¹ \n"
            f"3. {'Resistance:':<12}  [{self.resistance:>{longest}}] ⁺¹ \n"
            f"4. {'Crit:':<12}  [{self.crit:>{longest}}] ⁺¹\n"
            f"5. {'Luck:':<12}  [{self.luck:>{longest}}] ⁺¹\n"
            "```"
        )
        url = "https://cdn.discordapp.com/emojis/470326273298792469.png?v=1"
        embed.set_footer(
            text="You can not retrieve spent skillpoints!",
            icon_url=url
        )
        return embed
