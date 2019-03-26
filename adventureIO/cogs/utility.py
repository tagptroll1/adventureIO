from discord.ext.commands import Cog, command


class UtilityCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def rgbtohex(self, ctx, r: int, g: int, b: int):
        letter = {
            10: "A",
            11: "B",
            12: "C",
            13: "D",
            14: "E",
            15: "F",
        }
        r = r / 16
        g = g / 16
        b = b / 16
        r, r_ = int(r), int((r - int(r)) * 16)
        g, g_ = int(g), int((g - int(g)) * 16)
        b, b_ = int(b), int((b - int(b)) * 16)

        values = [r, r_, g, g_, b, b_]

        for i, value in enumerate(values):
            if int(value) > 9:
                values[i] = letter[value]

            values[i] = str(value)

        await ctx.send(f"#{''.join(values)}")

    @command()
    async def hextorgb(self, ctx, hex_):
        number_conv = {
            "A": 10,
            "B": 11,
            "C": 12,
            "D": 13,
            "E": 14,
            "F": 15
        }
        values = list(hex_.upper().replace("#", ""))

        for i, value in enumerate(values):
            if not value.isdigit():
                values[i] = number_conv[value]

        r = int(values[0]) * 16 + int(values[1])
        g = int(values[2]) * 16 + int(values[3])
        b = int(values[4]) * 16 + int(values[5])

        await ctx.send(f"R: {r}, G: {g}, B: {b}")


def setup(bot):
    bot.add_cog(UtilityCog(bot))