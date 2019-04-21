import logging
from pathlib import Path

from discord.ext.commands import Bot


log = logging.getLogger(__name__)


class AdventureBot(Bot):
    def __init__(self, db=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.load_extensions()

    async def on_message(self, message):

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
                    print(f"Loading... {path:<30} Success!")
                    log.info(f"Loading... {path:<30} Success!")
                except Exception:
                    log.exception(f"\nLoading... {path:<30} Failed!")
                    print(f"Loading... {path:<30} Failed!")
