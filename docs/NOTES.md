# Technical notes

The script (`src/map/war3map.j`) went through a map protector: function and variable names are obfuscated (`O77131`, `O214120`...). This is what has been figured out so far.

## Compatibility

### fix1: return bug
The map uses the JASS "return bug" to cast between types. Blizzard closed it in patch 1.24 ("Fixed the JASS unsafe type casting exploit"), which is why the map stopped loading. fix1 replaces those uses. Tested on 1.27b and Reforged.

### Editor files
The protector removed what the World Editor needs to open the map: `war3mapUnits.doo` was missing, `war3map.wtg` and `war3map.wct` were empty (0 bytes), and regions, cameras and sounds were missing. Rebuilt:
- `war3mapUnits.doo`: only the 9 start locations, taken from `config()` in the script.
- `wtg`, `wct`, `w3r`, `w3c`, `w3s`: valid but empty.

The game does not use these files: it creates everything from the script.

### 24 players (1.29+)
Before 1.29, players 12 to 15 were the neutral players; since 1.29 they are regular players and the neutrals moved to 24-27. **This map is not affected**:
- Literal `Player(12..15)` are used as scratch slots: storing strings in the player name, leaderboard rows, a temporary shop to measure item costs, and the anti-tamper check.
- Creeps belong to `Player(11)`.
- Neutral units use the game constants (`PLAYER_NEUTRAL_PASSIVE`, etc.), which adapt on their own.

### Balance data
Standard units that the map does not fully customize take the remaining values from the game. Both 1.27b and Reforged ship frozen data sets for custom maps: `Custom_V0` (Reign of Chaos) and `Custom_V1` (The Frozen Throne). Reforged also has the current melee balance.

`war3map.w3i` is version 25 (The Frozen Throne, editor 6052) even though the extension is `.w3m`.

`Custom_V1` from 1.27b compared with Reforged 3.0.1, for the 117 units the map uses and only the fields the map does not set:
- Units: 2 differences. Tauren (`otau`) and Spirit Wolf level 3 (`osw3`) gain Pillage (`asal`). Irrelevant for a TD.
- `Custom_V0`: no differences.
- Abilities: only new fields (empty → 0) and 3 minor changes in abilities the creeps do not use.
- Game constants (`MiscGame.txt`): only new keys.

With the current melee balance, creeps would change (Tauren speed 270→290, Abomination damage 32→34, Shaman 7→9, Lightning Lizard armor type, etc.).

**Confirmed on Reforged 3.0.1:** the builder, Warden of Souls (`u000`, based on the Acolyte), shows 0 armor and 220 HP, the frozen data values (current balance would give 1 and 230). Reforged loads `Custom_V1` for this map, so creeps have the same stats as on 1.27b.

### Souls display
Souls are the HP of the Tree of Souls. The leaderboard shows them with `R2SW(life, 0, 0)`; on Reforged they show with a decimal ("388.0").

## Anti-tamper check

Function `O211799`, called from `O211881` at startup. Compares:
- `TRIGSTR_001` (map name) with the copy stored in `Player(13)`'s name;
- `TRIGSTR_004` ("EnTrA1L") with `Player(14)`;
- `TRIGSTR_116` (description) with `Player(15)`.

If any of them does not match, it calls `EndGame`. The copies are encoded with a columnar transposition decoded by `O175508`, using the permutation `O6940` = 16, 2, 6, 8, 19, 17, 11, 12, 1, 3, 0, 9, 18, 7, 5, 10, 13, 4, 14, 15.

`tools/skname.py` reimplements the decoder (`decode`) and its inverse (`encode`). `build.py` uses it to change the map name without triggering the check. Author and description are never touched.

## Interface texts

- `war3mapSkin.txt` replaces interface strings with map strings. `UPKEEP_NONE=TRIGSTR_1229` is the top-right text, where "No upkeep" usually goes.
- Loading screen: title STRING 10, subtitle STRING 11 (also shown as the quest log header), text STRING 47.
- Leaderboard: title STRING 816, difficulty labels 1221-1223.

## Waves

- Wave counter per player: P1 `O77131`, P2 `O77154`, P3 `O77211`, P4 `O77705`, P5 `O77780`, P6 `O77811`, P7 `O77906`, P8 `O77966`.
- Each wave: the counter goes up by 1 and `O665[level]` spawns (20 creeps, one every 0.7 s; a single boss on 10, 20, 30, 40 and 50). When all die it gives level × 1 gold, waits 5 s and starts again. It stops at 50.
- Creeps per wave (`O665[n]`): 1 earc, 2 nwlg, 3 hpea, 4 uban, 5 esen, 6 ocat, 7 hmpr, 8 nltl, 9 nchg, 10 Hmkg, 11 nplg, 12 uabo, 13 nsrv, 14 hkni, 15 otau, 16 uktg, 17 emtg, 18 nckb, 19 uobs, 20 Eevi, 21 nsgg, 22 hmtm, 23 edoc, 24 oshm, 25 nhyc, 26 nsth, 27 odkt, 28 hmtt, 29 nfra, 30 Otch, 31 edot, 32 owar, 33 ucry, 34 nomg, 35 hspt, 36 umtw, 37 ohun, 38 Hvsh, 39 nsll, 40 Ucrl, 41 nmyr, 42 hrif, 43 nsgt, 44 osw3, 45 ntks, 46 hbew, 47 nehy, 48 nggr, 49 ninf, 50 Eidm.
- Events on exact levels: 6 and 16 (message + minimap ping), 22, 33 and 44 (invisible waves), 40 (global "Hurry Soulkeepers" message).

## Unused or removed code

- `thug4life` (in `O214120`): hidden author cheat, only for the red player and with no multiplayer guard. First use set gold to 55777; second use, if gold was still 55777, jumped to wave 49. Kept as the author made it.
- `O210599`: debug command kit (`gimme`, `demo`, `clone`, `fingerofdeath`, `blackmask`, `teleport`, camera...). Never called: dead code.
