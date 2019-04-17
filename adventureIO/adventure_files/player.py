# import adventureIO.database as database


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
    def from_database(cls, member, stats):
        (
            _, _, hp, max_hp,
            atk, res, crit, skillpoints,
            level, xp, money, activ,
        ) = stats

        player = cls(member)
        player.health = hp
        player.max_health = max_hp
        player.attack = atk
        player.resistance = res
        player.crit = crit
        player.skillpoints = skillpoints
        player.level = level
        player.xp = xp
        player.money = money
        player.activated = activ
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

        # TODO: Start session to add skillpoints to player
        # self.activated = True

    def revive(self):
        self.health = self.max_health
