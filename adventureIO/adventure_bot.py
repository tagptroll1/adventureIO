import logging
from pathlib import Path

from discord.ext.commands import Bot, command, group, is_owner

log = logging.getLogger(__name__)


class AdventureBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_extensions()

    async def on_message(self, message):
        print(message.content)

        await self.process_commands(message)

    def load_extensions(self):
        cogs = Path("./adventureIO/cogs")

        for cog in cogs.iterdir():
            if cog.is_dir():
                continue
            if cog.suffix == ".py":
                path = ".".join(cog.with_suffix("").parts)

                try:
                    self.load_extension(path)
                    print(f"Loading... {path:<22} Success!")
                    log.info(f"Loading... {path:<22} Success!")
                except Exception as e:
                    log.exception(f"\nLoading... {path:<22} Failed!")
                    print(f"Loading... {path:<22} Failed!")