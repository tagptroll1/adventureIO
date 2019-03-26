import logging
from pathlib import Path
from typing import List

import yaml


log = logging.getLogger(__name__)

if Path("config.yml").exists():
    with open("config.yml", encoding="UTF-8") as yml:
        config = yaml.safe_load(yml)


class YAMLGetter(type):
    def __getattr__(cls, name):
        name = name.lower()

        try:
            return config[cls.section][name]
        except KeyError:
            log.critical(f"Failed to load config[{cls.section}][{name}]")
            raise

    def __getitem__(cls, name):
        return cls.__getattr__(name)


class Bot(metaclass=YAMLGetter):
    section = "bot"

    token: str
    client_id: str
    prefix: str


class IDS(metaclass=YAMLGetter):
    section = "ids"

    creators: List[int]
    benny: int
