# Adventure database columns

-   player_id - int

-   type - string

-   running - bool

-   enemy_id - int

# Database methods

-   [ ] get_active_mob(mob_id: int) ->

    -   tuple(id:int, name:str, desc:str, hp:int, atk:int, res:int, crit:int, loot:int, max_hp:int)

-   [ ] async get_adventureres() ->

    -   AsyncIterator() -> dict("players_id": int, "type": str, "running": bool", "enemy_id": int, "max_hp": int)

-   [x] add_player(member_id: int, hp: int, max_hp: int, atk: int, res: int, crit: int, activated:bool)
    -   Modified to insert_player(pool, stats).
