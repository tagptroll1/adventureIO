import discord
import yaml

from adventureIO.constants import Emoji


with open("resources/monsters.yml", encoding="UTF-8") as yml:
    monsters = yaml.safe_load(yml)


class Monster:
    def __init__(self, name, desc, hp, atk, res, crit, loot, max_hp=None, **x):
        self.name = name
        self.description = desc
        self.max_hp = max_hp or hp
        self.health = hp
        self.attack = atk
        self.resistance = res
        self.crit = crit
        self.loot_table = loot
        self.thumbnail = monsters.get(self.name)["thumbnail"]

    @property
    def embed(self):
        embed = discord.Embed(title=self.name)
        embed.description = (
            f"{self.description}\n"
            " \n"
            f"<{Emoji.health}> {self.max_hp}\n"
            f"<{Emoji.attack}> {self.attack}\n"
            f"<{Emoji.resistance}> {self.resistance}\n"
            f"<{Emoji.crit}> {self.crit}\n"
        )
        embed.set_thumbnail(url=self.thumbnail)
        embed.color = discord.Colour.red()
        embed.set_footer(
            text=f"Type .adventure 1 to fight or .adventure 2 to flee"
        )
        return embed

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

    def to_json(self):
        return {
            "name": self.name,
            "desc": self.description,
            "hp": self.health,
            "atk": self.attack,
            "res": self.resistance,
            "crit": self.crit,
            "loot": self.loot_table,
        }
