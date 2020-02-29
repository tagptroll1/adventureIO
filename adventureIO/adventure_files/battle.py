import random

import discord

from adventureIO.constants import Emoji
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
        "desc": "It looks like a goblin.",
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

    def base_embed(self, title):
        embed = discord.Embed(title=title)
        embed.set_author(
            name=self.player.name,
            icon_url=self.player.member.avatar_url
        )
        embed.color = discord.Colour.gold()
        embed.set_thumbnail(url=self.enemy.thumbnail)

        return embed

    def battle_embed(self, report):
        player = self.player
        enemy = self.enemy
        embed = self.base_embed("Battle info")

        pcrit = "a critical hit of " if report["player_crit"] else ""
        mcrit = "a critical hit of " if report["monster_crit"] else ""

        description = (
            f"{player.name} rolled {pcrit}"
            f"<{Emoji.attack}>{report['player_dmg']}",

            f"{enemy.name} rolled {mcrit}"
            f"<{Emoji.attack}>{report['monster_dmg']}",
            " ",
            f"{player.name} has <{Emoji.health}>"
            f"{player.hp}/{player.max_hp} left.",

            f"{enemy.name} has <{Emoji.health}>"
            f"{enemy.hp}/{enemy.max_hp} left.\n "
        )
        embed.description = "\n".join(description)

        embed.set_footer(
            text=f"Type .adventure 1 to fight or .adventure 2 to flee"
        )

        return embed

    def win_embed(self, report):
        player = self.player
        enemy = self.enemy
        embed = self.base_embed("You win!")
        embed.color = discord.Color.green()

        pcrit = "a critical hit of " if report["player_crit"] else ""

        description = (
            f"{player.name} rolled {pcrit}"
            f"<{Emoji.attack}>{report['player_dmg']}",

            " ",
            f"{enemy.name} has been slain.",

            f"{player.name} has <{Emoji.health}>"
            f"{player.hp}/{player.max_hp} left.",
        )
        embed.description = "\n".join(description)

        embed.set_footer(
            text="You gained 5 xp, and looted 1 coin!"
        )

        return embed

    def lost_embed(self, report):
        player = self.player
        enemy = self.enemy
        embed = self.base_embed("You died")
        embed.color = discord.Color.red()

        pcrit = "a critical hit of " if report["player_crit"] else ""
        mcrit = "a critical hit of " if report["monster_crit"] else ""

        description = (
            f"{player.name} rolled {pcrit}"
            f"<{Emoji.attack}>{report['player_dmg']}",

            f"{enemy.name} rolled {mcrit}"
            f"<{Emoji.attack}>{report['monster_dmg']}",
            " ",
            f"{enemy.name} has <{Emoji.health}>"
            f"{enemy.hp}/{enemy.max_hp} left.",
            f"{player.name} was slain.."
        )

        embed.description = "\n".join(description)
        embed.set_footer(text="You can revive with .adventure revive")

        return embed

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

        if player.health > 0:
            return await self.battle_step(channel, report)
        else:
            return await self.player_died(channel, report)

    async def monster_died(self, channel, report):
        await channel.send(embed=self.win_embed(report))
        self.enemy = None
        return report["player_hp"]

    async def player_died(self, channel, report):
        await channel.send(embed=self.lost_embed(report))
        return 0

    async def battle_step(self, channel, report):
        await channel.send(embed=self.battle_embed(report))
        return self.player.health
