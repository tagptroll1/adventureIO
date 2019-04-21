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
                    f"{self.player.member.mention} you found a {mob.name}",
                    embed=mob.embed
                    )
                self.running = True

                return

        await self.continue_(ctx.channel, rest)

    def revive(self):
        if self.player.hp > 0:
            return True
            
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
                print(player, "died")
