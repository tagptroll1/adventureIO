import aiosqlite as asql
import collections
# import sqlite3 as sql


async def setup_tables(
    items=True,
    inventories=True,
    adventures=False,
    players=True
):
    if items:
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS items(
                    itemid INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INT DEFAULT 0,
                    weight INT DEFAULT 0,
                    rarity INT DEFAULT 1,
                    use_value INT DEFAULT 0,
                    use_value2 INT DEFAULT 0,
                    shop bool DEFAULT true
                );
            """
        )
        async with asql.connect("adventuredb.db") as db:
            await db.execute(SQL)
            await db.commit()

    if adventures:
        # adventureid is the id of the user holding it
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS adventures(
                    adventureid BIGINT PRIMARY KEY,
                    monsterid INTEGER
                );
            """
        )
        async with asql.connect("adventuredb.db") as db:
            await db.execute(SQL)
            await db.commit()

    if inventories:
        # Inventoryid is the id of the user holding it
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS inventories(
                    inventoryid BIGINT,
                    itemid INTEGER NOT NULL,
                    FOREIGN KEY(itemid)
                        REFERENCES items(itemid)
                );
            """
        )
        async with asql.connect("adventuredb.db") as db:
            await db.execute(SQL)
            await db.commit()

    if players:
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS players(
                    playerid BIGINT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    money INTEGER DEFAULT 0,
                    inventoryid INTEGER NOT NULL,
                    adventureid INTEGER NOT NULL,
                    FOREIGN KEY(inventoryid)
                        REFERENCES inventories(inventoryid),
                    FOREIGN KEY (adventureid)
                        REFERENCES adventures(adventureid)
                );
            """
        )
        async with asql.connect("adventuredb.db") as db:
            await db.execute(SQL)
            await db.commit()


async def check_item_exists(name):
    async with asql.connect("adventuredb.db") as db:
        async with db.execute(
                "SELECT * FROM items WHERE name=?;", (name,)) as curs:
            result = await curs.fetchone()

    if result:
        return result
    return False


async def delete_by_id(_id, table):
    id_column = table[:-1]+"id"
    SQL = f"DELETE FROM {table} where {id_column}=?"
    async with asql.connect("adventuredb.db") as db:
        await db.execute(SQL, (_id,))
        await db.commit()


async def delete_by_name(name, table):
    SQL = f"DELETE FROM {table} where name=?"
    async with asql.connect("adventuredb.db") as db:
        await db.execute(SQL, (name,))
        await db.commit()


async def add_item(
    name,
    _id=None,
    price=None,
    weight=None,
    rarity=None,
    shop=True,
    use1=None,
    use2=None
):
    SQL = "INSERT INTO items ("

    if _id:
        SQL += "id, name"
        values = [_id, name]
    else:
        SQL += "name"
        values = [name]

    if price:
        SQL += ", price"
        values.append(price)

    if weight:
        SQL += ", weight"
        values.append(weight)

    if rarity:
        SQL += ", rarity"
        values.append(rarity)

    if use1:
        SQL += ", use_value"
        values.append(use1)

        if use2:
            SQL += ", use_value2"
            values.append(use2)

    else:
        if use2:
            SQL += ", use_value"
            values.append(use2)

    SQL += ", shop"
    values.append(shop)

    SQL += f") VALUES (?{', ?'*(len(values)-1)});"

    async with asql.connect("adventuredb.db") as db:
        await db.execute(SQL, values)
        await db.commit()


class AllItems:
    def __init__(self):
        self.buffer = collections.deque()
        self.first_iter = True

    async def _prefetch(self):
        SQL = "SELECT * FROM items;"
        async with asql.connect("adventuredb.db") as db:
            async with db.execute(SQL) as cursor:
                results = await cursor.fetchall()

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
    def __init__(self):
        self.buffer = collections.deque()
        self.first_iter = True

    async def _prefetch(self):
        SQL = "SELECT * FROM players;"
        async with asql.connect("adventuredb.db") as db:
            async with db.execute(SQL) as cursor:
                results = await cursor.fetchall()

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
