import random

from .battle import Battle


BATTLE = 1
ADVENTURE_TYPES = (BATTLE, BATTLE)


class Adventure:
    def __init__(self, player):
        self.player = player
        self.type = None
        self.running = False
        self.instance = None

    async def start(self, ctx, rest):
        self.type = random.choice(ADVENTURE_TYPES)

        if self.type == BATTLE:
            if self.instance is None:
                self.instance = Battle(self.player, ctx)
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

        await self.continue_(ctx, rest)

    def revive(self):
        self.player.revive()
        self.running = False
        self.type = None
        self.instance = None

    async def continue_(self, ctx, rest):
        if self.player.hp <= 0:
            await ctx.send("You are dead... Revive to adventure!")
            return

        if self.type == BATTLE:
            if self.instance is None:
                self.instance = Battle(self.player, ctx)
                await self.instance.setup()

            self.hp = await self.instance.step()

            if not self.instance.enemy:
                self.instance = None
                self.running = False
                self.type = None
            elif self.player.health <= 0:
                await ctx.send("Lol...")
