import random

from discord.ext.commands import Cog, group

# import adventureIO.database as database


BATTLE = 1
ADVENTURE_TYPES = (BATTLE, BATTLE)

BOAR = 1
GOBLIN = 2
ENEMIES = (BOAR, GOBLIN)

PLAYER = {
    "name": "Player",
    "desc": "Temp player stats",
    "hp": 10,
    "atk": 4,
    "res": 5,
    "crit": 5,
}

TEMP_MONSTER_STATS = {
    1: {
        "name": "Boar",
        "desc": "It's part of the pig family",
        "hp": 10,
        "atk": 2,
        "res": 3,
        "crit": 1,  # 0 - 100 %
        "loot": 1,
    },
    2: {
        "name": "Goblin",
        "desc": "It looks like David.",
        "hp": 50,
        "atk": 3,
        "res": 2,
        "crit": 2,
        "loot": 2,
    }
}


class AdventureCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_adventures = {}

        # bot.loop.create_task(self.sync_adventures())

    async def sync_adventures(self):
        ...
        # adventurers = await database.get_adventurers()

    @group(name="adventure", aliases=("adv", "a"), invoke_without_command=True)
    async def adventure_group(self, ctx, *, rest=None):

        await ctx.invoke(self.adventure_alt_1, rest=rest)

    @adventure_group.command(name="1")
    async def adventure_alt_1(self, ctx, *, rest=None):
        author = ctx.author

        if author.id not in self.active_adventures:
            adventure = Adventure(author)
            self.active_adventures[author.id] = adventure
        else:
            adventure = self.active_adventures.get(author.id)

        if adventure.running:
            await adventure.continue_(ctx, rest)
        else:
            await adventure.start(ctx, rest)

    @adventure_group.command(name="revive")
    async def adventure_revive(self, ctx):
        adventure = self.active_adventures.get(ctx.author.id)
        if adventure:
            adventure.revive()
            await ctx.send("Revived")
        else:
            await ctx.send("You don't even have an advanture going..")


class Adventure:
    def __init__(self, player):
        self.player = player
        self.type = None
        self.running = False
        self.instance = None
        self.hp = PLAYER["hp"]

    async def start(self, ctx, rest):
        self.type = random.choice(ADVENTURE_TYPES)
        self.running = True

        await self.continue_(ctx, rest)

    def revive(self):
        print(PLAYER["hp"])
        self.hp = PLAYER["hp"]
        self.running = False
        self.type = None
        self.instance = None

    async def continue_(self, ctx, rest):
        if self.type == BATTLE:
            if self.instance is None:
                self.instance = Battle(self.player, ctx, self.hp)
                await self.instance.setup()

            self.hp = await self.instance.step()

            if not self.instance.enemy:
                self.instance = None
                self.running = False
                self.type = None
            elif self.hp <= 0:
                await ctx.send("Lol...")


class Battle:
    def __init__(self, player, ctx, hp=None):
        self.player = player
        self.max_hp = PLAYER["hp"]
        self.hp = hp or self.max_hp  # Hardcoded for now
        self.ctx = ctx
        self.enemy = None

    async def setup(self):
        # TODO: Enemy from db
        monster_id = random.choice(ENEMIES)
        stats = TEMP_MONSTER_STATS[monster_id]
        self.enemy = Monster(**stats)

    async def step(self):
        monster = self.enemy
        monster_crit = random.randint(0, 100) <= self.enemy.crit
        monster_dmg = monster.atk * 20 if monster_crit else monster.atk * 10

        # Player hardcoded stats for now.
        player_crit = random.randint(0, 100) <= PLAYER["crit"]
        player_dmg = PLAYER["atk"] * 20 if player_crit else PLAYER["atk"] * 10

        monster.health -= player_dmg // 10

        report = {
            "player_dmg": player_dmg,
            "player_crit": player_crit,
            "monster_hp": monster.health,
            "player_hp": self.hp
        }

        if monster.health <= 0:
            return await self.monster_died(report)

        self.hp -= monster_dmg // 10

        report["monster_dmg"] = monster_dmg
        report["monster_crit"] = monster_crit
        report["player_hp"] = self.hp

        return await self.print_battlestatus(report)

    async def monster_died(self, report):
        monster = self.enemy
        name = self.player.display_name
        if report["player_crit"]:
            crit = "with a critial blow"
        else:
            crit = ""

        await self.ctx.send(
            f"{name} hit {monster.name} {crit} for {report['player_dmg']}\n"
            f"{monster.name} was slain! \n"
            f"{name} has "
            f"{report['player_hp']*10}/{self.max_hp*10} hp left."
        )
        self.enemy = None
        return report["player_hp"]

    async def player_died(self, report):
        monster = self.enemy
        await self.ctx.send(
            f"{self.player.display_name} was slain by "
            f"{monster.name}.\n"
        )
        return 0

    async def print_battlestatus(self, report):
        monster = self.enemy
        name = self.player.display_name
        m_dmg = report["monster_dmg"]
        p_dmg = report["player_dmg"]

        if report["player_crit"]:
            crit = "with a critial blow"
        else:
            crit = ""

        if report["monster_crit"]:
            m_crit = "with a powerful strike"
        else:
            m_crit = ""

        response = (
            f"{name} hit {monster.name} {crit} for {p_dmg}\n"
            f"{monster.name} hit {name} {m_crit} for {m_dmg}\n"
            f"{monster.name} has "
            f"{monster.hp*10}/{monster.max_hp*10} hp left."
        )

        if self.hp > 0:
            response += (
                f"\n{name} has "
                f"{report['player_hp']*10}/{self.max_hp*10} hp left."
            )
            await self.ctx.send(response)
            return self.hp
        else:
            await self.ctx.send(response)
            return await self.player_died(report)


class Monster:
    def __init__(self, name, desc, hp, atk, res, crit, loot):
        self.name = name
        self.description = desc
        self.max_hp = hp
        self.health = hp
        self.attack = atk
        self.resistance = res
        self.crit = crit
        self.loot_table = loot

    @property
    def hp(self):
        return self.health

    @property
    def desc(self):
        return self.description

    @property
    def atk(self):
        return self.attack

    @property
    def res(self):
        return self.resistance

    @property
    def loot(self):
        return self.loot_table


def setup(bot):
    bot.add_cog(AdventureCog(bot))
