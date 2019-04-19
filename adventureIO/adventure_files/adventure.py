import random

from .battle import Battle


BATTLE = 1
ADVENTURE_TYPES = (BATTLE, BATTLE)


class Adventure:
    def __init__(self, player, type=None, running=False, instance=None):
        self.player = player
        self.type = None
        self.running = False
        self.instance = None

    async def start(self, ctx, rest):
        self.type = random.choice(ADVENTURE_TYPES)

        if self.type == BATTLE:
            if self.instance is None:
                self.instance = Battle(self.player)
                await self.instance.setup()

                mob = self.instance.enemy
                await ctx.send(
                    f"You ran into a {mob.name}.\n"
                    f"{mob.hp}\n"
                    f"{mob.desc}\n\n"
                    f"Type {ctx.prefix}adventure 1 to fight, 2 to flee"
                )
                self.running = True

                return

        await self.continue_(ctx.channel, rest)

    def revive(self):
        self.player.revive()
        self.running = False
        self.type = None
        self.instance = None

    async def continue_(self, channel, rest):
        if self.player.hp <= 0:
            await channel.send("You are dead... Revive to adventure!")
            return

        if self.type == BATTLE:
            if self.instance is None:
                self.instance = Battle(self.player)
                await self.instance.setup()

            self.hp = await self.instance.step(channel)

            if not self.instance.enemy:
                self.instance = None
                self.running = False
                self.type = None
            elif self.player.health <= 0:
                await channel.send("Lol...")
