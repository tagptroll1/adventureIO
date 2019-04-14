import random

from .monster import Monster

BOAR = 1
GOBLIN = 2
ENEMIES = (BOAR, GOBLIN)

PLAYER = {
    "name": "Player",
    "desc": "Temp player stats",
    "hp": 20,
    "atk": 4,
    "res": 5,
    "crit": 5,
}

TEMP_MONSTER_STATS = {
    1: {
        "name": "Boar",
        "desc": "It's part of the pig family",
        "hp": 50,
        "atk": 2,
        "res": 3,
        "crit": 1,  # 0 - 100 %
        "loot": 1,
    },
    2: {
        "name": "Goblin",
        "desc": "It looks like David.",
        "hp": 100,
        "atk": 3,
        "res": 2,
        "crit": 2,
        "loot": 2,
    }
}


class Battle:
    def __init__(self, player, enemy=None):
        self.player = player
        self.enemy = enemy

    async def setup(self):
        # TODO: Enemy from db
        monster_id = random.choice(ENEMIES)
        stats = TEMP_MONSTER_STATS[monster_id]
        self.enemy = Monster(**stats)

    @staticmethod
    def get_roll(attack):
        roll_scale = random.randint(0, 10)

        if roll_scale <= 2:  # low roll
            low = 0 if attack <= 2 else attack - 3
            high = 1 if attack <= 1 else attack - 1
        elif roll_scale >= 8:  # high roll
            low = attack
            high = attack + 4
        else:  # average
            low = 0 if attack <= 1 else attack - 2
            high = attack + 2

        return random.randint(low, high)

    @staticmethod
    def get_crit(dmg, crit):
        if crit:
            return dmg * 2
        return dmg

    @staticmethod
    def get_damage(user):
        dice = Battle.get_roll(user.atk)
        crit = random.randint(0, 100) <= user.crit
        dmg = Battle.get_crit(user.atk, crit)

        return dmg * dice, crit

    async def step(self, channel):
        print("Step called")
        monster = self.enemy
        m_dmg, m_crit = self.get_damage(monster)

        player = self.player
        p_dmg, p_crit = self.get_damage(player)

        monster.health -= p_dmg

        report = {
            "player_dmg": p_dmg,
            "player_crit": p_crit,
            "monster_hp": monster.health,
            "player_hp": player.health
        }

        if monster.health <= 0:
            return await self.monster_died(channel, report)

        player.health -= m_dmg

        report["monster_dmg"] = m_dmg
        report["monster_crit"] = m_crit
        report["player_hp"] = player.health

        return await self.print_battlestatus(channel, report)

    async def monster_died(self, channel, report):
        monster = self.enemy
        name = self.player.display_name

        if report["player_crit"]:
            crit = "with a critial blow"
        else:
            crit = ""

        await channel.send(
            f"{name} hit {monster.name} {crit} for {report['player_dmg']}\n"
            f"{monster.name} was slain! \n"
            f"{name} has "
            f"{report['player_hp']}/{self.player.max_hp} hp left."
        )
        self.enemy = None
        return report["player_hp"]

    async def player_died(self, channel, report):
        monster = self.enemy
        await channel.send(
            f"{self.player.display_name} was slain by "
            f"{monster.name}.\n"
        )
        return 0

    async def print_battlestatus(self, channel, report):
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
            f"{monster.hp}/{monster.max_hp} hp left."
        )

        if self.player.hp > 0:
            response += (
                f"\n{name} has "
                f"{report['player_hp']}/{self.player.max_hp} hp left."
            )
            await channel.send(response)
            return self.player.hp
        else:
            await channel.send(response)
            return await self.player_died(channel, report)
