import collections

import asyncpg


class Database:
    def __init__(self, pool):
        self.pool = pool

    async def setup_tables(
        self,
        items=True,
        inventories=True,
        adventures=False,
        players=True
    ):
        if players:
            SQL = (
                """
                    CREATE TABLE IF NOT EXISTS player(
                        playerid BIGINT PRIMARY KEY,
                        name TEXT NOT NULL,
                        hp INTEGER DEFAULT 30,
                        maxhp INTEGER DEFAULT 30,
                        atk INTEGER DEFAULT 5,
                        res INTEGER DEFAULT 5,
                        crit INTEGER DEFAULT 1,
                        luck INTEGER DEFAULT 0,
                        skillpoints INTEGER DEFAULT 5,
                        level INTEGER DEFAULT 1,
                        xp INTEGER DEFAULT 0,
                        money INTEGER DEFAULT 0,
                        activated BOOLEAN DEFAULT FALSE,
                        adventureid BIGINT DEFAULT NULL
                    );
                """
            )

            async with self.pool.acquire() as conn:
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
            async with self.pool.acquire() as conn:
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
            async with self.pool.acquire() as conn:
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

            async with self.pool.acquire() as conn:
                await conn.execute(SQL)

    async def fetch_player(self, id_, conn=None):
        SQL = "SELECT * FROM player WHERE playerid = $1;"

        if conn:
            result = await conn.fetchrow(SQL, id_)
        else:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(SQL, id_)

        return result

    async def update_player(self, player):
        SQL = (
            """
            UPDATE player
                SET 
                    hp = $2,
                    maxhp = $3,
                    atk = $4,
                    res = $5,
                    crit = $6,
                    luck = $7,
                    skillpoints = $8,
                    level = $9,
                    xp = $10,
                    money = $11,
                    activated = $12,
                    adventureid = $13
                WHERE playerid = $1
            """
        )

        async with self.pool.acquire() as conn:
            await conn.execute(SQL, *player.row)

    async def insert_player(self, stats):
        async with self.pool.acquire() as conn:
            SQL = (
                """
                INSERT INTO player(
                    playerid, name
                ) VALUES ($1, $2);
                """
            )
            try:
                await conn.execute(
                    SQL, stats["playerid"], stats["name"]
                    )
            except asyncpg.UniqueViolationError:
                return False
            return True

    async def check_item_exists(self, name):
        async with self.pool.acquire() as conn:
            SQL = "SELECT * FROM item WHERE name=$1;"
            result = await conn.fetchrow(SQL, *(name,))

        if result:
            return result
        return False

    async def delete_by_id(self, _id, table):
        id_column = table + "id"
        SQL = f"DELETE FROM {table} where {id_column}=$1;"

        async with self.pool.acquire() as conn:
            await conn.execute(SQL, *(_id,))

    async def delete_by_name(self, name, table):
        SQL = f"DELETE FROM {table} where name=$1;"

        async with self.pool.acquire() as conn:
            await conn.execute(SQL, *(name,))

    async def delete_many_by_id(self, ids, table):
        assert isinstance(ids, (list, tuple, set))

        ids = [(id_,) for id_ in ids]

        id_column = table[:-1] + "id"
        SQL = f"DELETE FROM {table} where {id_column}=$1;"

        async with self.pool.acquire() as conn:
            await conn.executemany(SQL, ids)

    async def delete_many_by_name(self, names, table):
        assert isinstance(names, (list, tuple, set))

        names = [(name,) for name in names]

        SQL = f"DELETE FROM {table} where name=$1;"

        async with self.pool.acquire() as conn:
            await conn.executemany(SQL, names)

    async def add_item(
        self,
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

        async with self.pool.acquire() as conn:
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
