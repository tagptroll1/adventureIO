
import asyncpg
import collections
import urllib.parse as up

from adventureIO.constants import Database
# import sqlite3 as sql

up.uses_netloc.append("postgres")
url = up.urlparse(Database.url)

path = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port


async def get_pool():
    pool = await asyncpg.create_pool(
        user=user,
        password=password,
        database=path,
        host=host,
        port=port,
        min_size=4,
        max_size=4
    )
    return pool


async def setup_tables(
    bot,
    items=True,
    inventories=True,
    adventures=False,
    players=True
):

    if not hasattr(bot, "pool"):
        return

    pool = bot.pool

    if players:
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS player(
                    playerid BIGINT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    money INTEGER DEFAULT 0,
                    inventoryid int,
                    adventureid int
                );
            """
        )

        async with pool.acquire() as conn:
            await conn.execute(SQL)

    if adventures:
        # adventureid is the id of the user holding it
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS adventure(
                    adventureid BIGINT PRIMARY KEY,
                    monsterid INTEGER
                );
            """
        )
        async with pool.acquire() as conn:
            await conn.execute(SQL)

    if inventories:
        # Inventoryid is the id of the user holding it
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS inventory(
                    owner_id BIGINT PRIMARY KEY,
                    owner BIGINT REFERENCES player(playerid)
                );
            """
        )
        async with pool.acquire() as conn:
            await conn.execute(SQL)

    if items:
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS item(
                    itemid SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INT DEFAULT 0,
                    weight INT DEFAULT 0,
                    rarity INT DEFAULT 1,
                    use_value INT DEFAULT 0,
                    use_value2 INT DEFAULT 0,
                    shop bool DEFAULT true,
                    inventoryid BIGINT REFERENCES inventory(owner_id)
                );
            """
        )

        async with pool.acquire() as conn:
            await conn.execute(SQL)


async def check_item_exists(pool, name):
    async with pool.acquire() as conn:
        SQL = "SELECT * FROM item WHERE name=$1;"
        result = await conn.fetchrow(SQL, *(name,))

    if result:
        return result
    return False


async def delete_by_id(pool, _id, table):
    id_column = table[:-1]+"id"
    SQL = f"DELETE FROM {table} where {id_column}=$1;"

    async with pool.acquire() as conn:
        await conn.execute(SQL, *(_id,))


async def delete_by_name(pool, name, table):
    SQL = f"DELETE FROM {table} where name=$1;"

    async with pool.acquire() as conn:
        await conn.execute(SQL, *(name,))


async def delete_many_by_id(pool, ids, table):
    assert isinstance(ids, (list, tuple, set))

    ids = [(id_,) for id_ in ids]

    id_column = table[:-1] + "id"
    SQL = f"DELETE FROM {table} where {id_column}=$1;"

    async with pool.acquire() as conn:
        await conn.executemany(SQL, ids)


async def delete_many_by_name(pool, names, table):
    assert isinstance(names, (list, tuple, set))

    names = [(name,) for name in names]

    SQL = f"DELETE FROM {table} where name=$1;"

    async with pool.acquire() as conn:
        await conn.executemany(SQL, names)


async def add_item(
    pool,
    name,
    _id=None,
    price=None,
    weight=None,
    rarity=None,
    shop=True,
    use1=None,
    use2=None
):
    SQL = "INSERT INTO item ("

    if _id:
        SQL += "id, name"
        values = [int(_id), name]
    else:
        SQL += "name"
        values = [name]

    if price:
        SQL += ", price"
        values.append(int(price))

    if weight:
        SQL += ", weight"
        values.append(int(weight))

    if rarity:
        SQL += ", rarity"
        values.append(int(rarity))

    if use1:
        SQL += ", use_value"
        values.append(int(use1))

        if use2:
            SQL += ", use_value2"
            values.append(int(use2))

    else:
        if use2:
            SQL += ", use_value"
            values.append(int(use2))

    SQL += ", shop"
    values.append(shop)

    dollars = ", ".join([f"${i}" for i in range(1, len(values) + 1)])
    SQL += f") VALUES ({dollars});"

    async with pool.acquire() as conn:
        await conn.execute(SQL, *values)


class AllItems:
    def __init__(self, pool):
        self.pool = pool
        self.buffer = collections.deque()
        self.first_iter = True

    async def _prefetch(self):
        SQL = "SELECT * FROM item;"

        async with self.pool.acquire() as conn:
            results = await conn.fetch(SQL)

        self.first_iter = False
        return collections.deque(results)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.buffer:
            if not self.first_iter:
                raise StopAsyncIteration

            self.buffer = await self._prefetch()

            if not self.buffer:
                raise StopAsyncIteration

        return self.buffer.popleft()


class AllPlayers:
    def __init__(self, pool):
        self.pool = pool
        self.buffer = collections.deque()
        self.first_iter = True

    async def _prefetch(self):
        SQL = "SELECT * FROM player;"

        async with self.pool.acquire() as conn:
            results = await conn.fetch(SQL)

        self.first_iter = False
        return collections.deque(results)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.buffer:
            if not self.first_iter:
                raise StopAsyncIteration

            self.buffer = await self._prefetch()

            if not self.buffer:
                raise StopAsyncIteration

        return self.buffer.popleft()
