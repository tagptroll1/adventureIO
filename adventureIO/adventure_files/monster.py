
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
