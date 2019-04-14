# Adventure database columns

* player_id - int

* type - string

* running - bool

* enemy_id - int

  

# Database methods

- [ ] get_active_mob(mob_id: int) -> 
  - tuple(id:int, name:str, desc:str, hp:int, atk:int, res:int, crit:int, loot:int, max_hp:int)

- [ ] async get_adventurerers() ->
  * AsyncIterator() -> dict("players_id": int, "type": str, "running": bool", "enemy_id": int, "max_hp": int)

- [ ] add_player(member_id: int, hp: int, max_hp: int, atk: int, res: int, crit: int, activated:bool)