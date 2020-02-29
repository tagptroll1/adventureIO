# Adventure database columns

-   player_id - int
-   type - string
-   running - bool
-   enemy_id - int

# Player database columns

* playerid - id
* name - string
* hp - int
* maxhp - int
* atk - int
* res - int
* crit - int
* luck - int
* skillpoints - int
* level - int
* xp - int
* money - int
* activated - bool
* adventureid - id

# Item database columns

* itemid - serial
* name - string
* price - int
* weight - int
* rarity - int (1 - 5?)
* use_value - int
* use_value2 - int
* shop - bool (bought from vendor?)
* inventoryid - id

# Database methods

-   [ ] get_active_mob(mob_id: int) ->

    -   tuple(id:int, name:str, desc:str, hp:int, atk:int, res:int, crit:int, loot:int, max_hp:int)

-   [ ] async get_adventureres() ->

    -   AsyncIterator() -> dict("players_id": int, "type": str, "running": bool", "enemy_id": int, "max_hp": int)

-   [x] add_player(member_id: int, hp: int, max_hp: int, atk: int, res: int, crit: int, activated:bool)
    -   Modified to insert_player(pool, stats)
    -   [x] push player to database
    -   [x] activate players
        -   [ ] Inform player how to add skillpoints and how to get help.
    -   [x] display all players
    -   [ ] search players
-   [x] fetch_player(pool, id)



- [x] Adventure cog doesn't need to load adventures and players on creation
- [ ] Each adventure needs to be pushed through the queue function when it's needed,  This has to fetch from the database first to ensure synced data.  
- [ ] All actions that change the player needs to be queued in a temp cache that executes many every minute or so, and the bot has to enforce this is saved before it shuts down.  Preferably caught Keyboard interrupt as well.
- [ ] Decide if activate is really needed?
- [ ] Separate adventure types
- [ ] Get exp from kills
- [ ] get money from kills
- [ ] linear leveling with modulus or increase the level attribute with an exponential xp need.
- [ ] adventure alternatives with different stories and paths
- [ ] potions and shop
- [ ] longer cooldown events like mining, chopping, fishing
- [ ] revive costs x% of xp and money, and revives with 50% of total hp.
- [ ] aliases for adventure options
- [ ] timeout dev add item 

bug:
    - Create says an account already exists on first use
        - If timeout timeouts you cant add skillspoints
        - not activated and revive throws coroutine doesnt have activated attr `line 139, if not player.activated`
        - queue saves the one being pushed, not the popped?
put mention in response