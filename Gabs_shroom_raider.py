import os
import sys
from time import sleep  # execution delays for "animations"

delay = 0.05

# ---------------------------------------------------------------------
# GAME LOOP

# 1.) move

# this func prints to terminal and contains the main loop

# 2.) accept and assess valid inputs:

# moves via move_check func
# picking up items via pickup func
# (all changes are made by editing leveldata var)

# 3.) helper funcs to manipulate leveldata other than laro

# includes:
# push func
# use_item and flamethrower funcs

# 4.) return to move to receive next inputs, repeat until end condition
# ---------------------------------------------------------------------

# Graphics from ASCII and text to UI
Ui = {".": '  ',
    "L": '🧑',
    "T": '🌲',
    "+": '🍄',
    "R": '🪨',
    "~": '🟦',
    "_": '⬜',
    "x": '🪓',
    "*": '🔥',
    "=": '📦',
    "#": '🧱',
    "P": "🔨",
    "Axe": '🪓',
    "Flamethrower": '🔥',
    "Hammer": "🔨"}

# Readability: constant vars for leveldata items
empty = "."
laro = "L"
mushroom = "+"
tree = "T"
rock = "R"
water = "~"
paved = "_"
axe = "x"
fire = "*"
crate = "="
wall = "#"
hammer = "P"

# Item attributes
pushable = (rock, crate)
unpushable = (wall, tree) # *Without items
items = (axe, fire, hammer)

flammable = (tree, crate)
hammerable = (wall, rock)

tree_tools = ('Axe', 'Flamethrower')
stone_tools = ('Hammer',)


LEVEL = ''
DEMOLEVEL = '''\
TTTTTTTTTTT
T...T+T...T
T.*.T~T.x.T
T.TT.~....T
T.T+TL.*..T
T.TTT.....T
T..R...R~~T
T.......~+T
TTTTTTTTTTT'''


def clear() -> None:
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

def print_to_terminal(levelgrid : list): # Local func to print to terminal
        level = [''.join(Ui[x] for x in y) for y in levelgrid]
        level = '\n'.join(level)
        print(level + '\n')


def main() -> (str, str):
    # Checks if there is a level inputted along with the command, loads the demo otherwise
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], encoding='utf-8') as f:
                return (f.read(), sys.argv[2])
        except FileNotFoundError:
            print('Level file not found')
            sys.exit()
    else:
        return (DEMOLEVEL, 'demo_level.txt')


(LEVEL, LEVEL_NAME) = main()


# Leaderboards per level are stored in a separate .txt file
# Entries are stored as: NAME, MOVES, RANK
def show_leaderboard() -> None:
    if len(sys.argv) >= 3:
        level_name = sys.argv[2]
        ld_file = f'{level_name}_leaderboard.txt'
    else:
        ld_file = 'demo_level_leaderboard.txt'
    try:
        with open(ld_file, encoding="utf-8") as f:
            leaderboard_raw = f.read()
        if not leaderboard_raw:
            print(f'No scores found for {LEVEL_NAME}.')
            sys.exit()
        else:
            leaderboard_past = leaderboard_raw.split('\n')
            leaderboard_past = list(tuple(ld.split(', ')) for ld in leaderboard_past)
            leaderboard = {n[1:-1]: (int(moves), int(s)) for n, moves, s in leaderboard_past}
    except FileNotFoundError:
        print(f'No scores found for {LEVEL_NAME}.')
        sys.exit()
    print(f'Displaying leaderboard for {LEVEL_NAME}')
    print('''
RANK    NAME            MOVES''')
    name_order = [name for name in leaderboard]
    names_len = len(name_order)
    names_len = min(10, names_len)
    for n in range(names_len):
        n1 = n+1
        sp = '  ' if n1 == 10 else ' '
        nm = name_order[n]
        (moves, s) = leaderboard[nm]
        print(f'{n1}{sp}' + f'     {nm}' + ' '*(8 - len(nm)) + '        ' + f'{moves}')

# LEVELDATA
# Reads the level and makes leveldata


def create_leveldata(level: str) -> dict:
    levelgrid = level.split('\n')
    result = {
        'borders': (0, 0),
        'laro': (0, 0),
        'laro_initial': (0, 0),
        'mush_collected': 0,
        'mush_total': 0,
        'paved': (),
        'standing_on': '.',
        'holding': '',
        'move_count': 0,
        'control_scheme': ()}
    (r, c) = (len(levelgrid), len(levelgrid[0]))
    result['borders'] = (r, c)
    # Obtain in-level tile data
    for i in range(r):
        for j in range(c):
            tile = levelgrid[i][j]
            if tile == mushroom:
                result['mush_total'] += 1
            elif tile == 'L':
                result['laro'] = (i, j)
                result['laro_intial'] = (i, j)
    control_scheme_choice = {
        'w': ('W', 'A', 'S', 'D'),
        'u': ('U', 'L', 'D', 'R')}
    clear()
    while True:
        with open("menu.txt", encoding='utf-8') as m:
            choice = input(m.read() + '\n\n')
        if choice in {'w', 'W', 'u', 'U'}:
            result['control_scheme'] = control_scheme_choice[choice.lower()]
            break
        if choice.lower() == "q":
            clear()
            sys.exit()
        elif choice.lower() == "l":
            show_leaderboard()
            sys.exit()
        else:
            print('Invalid input. Try again')
    return result


LEVELDATA = create_leveldata(LEVEL)

lv = LEVEL

lvd = {}
for x in LEVELDATA:
    lvd[x] = LEVELDATA[x]




def move(level: str, leveldata: dict) -> None:
        
    levelgrid = level.split('\n')
    levelgrid = [list(x) for x in levelgrid]
    while True:
        
        for r, c in leveldata['paved']:
            if levelgrid[r][c] == '.':
                levelgrid[r][c] = '_'
            (laro_r, laro_c) = leveldata['laro']
        # Update level data
        (laro_r, laro_c) = leveldata['laro']
        # Check for win condition
        if leveldata['mush_collected'] == leveldata['mush_total']:
            endscreen(leveldata, levelgrid)
            
        # Print to terminal
        clear()
        print_to_terminal(levelgrid)
        # Change pickup button text based on current holding and stood-on items
        (pickup_info, item) = ("", leveldata['standing_on'])
        if leveldata['standing_on'] in items:
            if not leveldata['holding']:
                pickup_info = "[P] = PICK UP " + item.upper() + " (" + Ui[item] + ")"
            else:
                pickup_info = "      ON TOP OF " + item.upper() + " (" + Ui[item] + ")"
        # Add text for items held, if any
        (holding_info, item) = ("", leveldata['holding'])
        if leveldata['holding']:
            holding_info = "You're holding a " + item.lower() + " (" + Ui[item] + ")"
        steps = input(f'''\
{leveldata['mush_collected']}/{leveldata['mush_total']} {Ui["+"]} collected
{holding_info}

[{leveldata['control_scheme'][0]}] = UP
[{leveldata['control_scheme'][1]}] = LEFT
[{leveldata['control_scheme'][2]}] = DOWN
[{leveldata['control_scheme'][3]}] = RIGHT
{pickup_info}

[!] = RESET
[Q] = EXIT

Enter your next move/s: ''')

        if len(steps) == 1:
            animation_delay = False
        else:
            animation_delay = True
            

        # Run step by step
        for step in steps:
            (laro_r, laro_c) = leveldata['laro']
            
            clear()
            print_to_terminal(levelgrid)
            if animation_delay:
                sleep(delay)
                
            step = step.upper()
            if step.isalpha():

                sleep(delay)

                # Assess valid inputs
                if step in leveldata['control_scheme']:
                    (level, leveldata) = move_check(levelgrid, leveldata, step)
                elif step == 'P':  # Pickup
                    if leveldata['standing_on'] and not leveldata['holding']:
                        leveldata = pick_up(leveldata)
                elif step == 'Q':
                    clear()
                    sys.exit()

            # Fixes bug that retains Laro's position from last run
            elif step == '!':
                leveldata = {}
                for x in LEVELDATA:
                    leveldata[x] = LEVELDATA[x]
                levelgrid = LEVEL.split('\n')
                levelgrid = [list(x) for x in levelgrid]
            # Invalid key: end loop prematurely
            else:
                break

# Str tile_to_move is a control key
# Dict neighbors has control keys as keys, and new tile positions from those keys as values
def move_check(level: str, leveldata: dict, tile_to_move: str) -> (str, dict):
    leveldata['move_count'] += 1
    (r, c) = leveldata['laro']
    neighbors = {
        leveldata['control_scheme'][0]: (r-1, c),
        leveldata['control_scheme'][2]: (r+1, c),
        leveldata['control_scheme'][1]: (r, c-1),
        leveldata['control_scheme'][3]: (r, c+1)}

    # Tile Laro is about to move to, used to check what kind of tile laro is about to run to
    (r1, c1) = neighbors[tile_to_move]
    if not out_of_borders(r1, c1, leveldata['borders']):
        return (level, leveldata)

    target_tile = level[r1][c1]
    held_item = leveldata['holding']

    # Check all item interactions first
    if target_tile == tree and held_item in tree_tools: # Trees
        return use_item(level, leveldata, (r1, c1))

    elif target_tile in hammerable and held_item in stone_tools: # Walls, rocks
        return use_item(level, leveldata, (r1, c1))

    elif target_tile in pushable: # Runs push() command
        return push(level, leveldata, tile_to_move)  

    # Case: nothing happens, from not having the right item
    elif target_tile in unpushable: 
        return (level, leveldata)

    # Now check for working itemless conditions
    elif target_tile == mushroom:
        leveldata['mush_collected'] += 1
        level[r][c] = '.'
        level[r1][c1] = 'L'
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)
    
    elif target_tile == water:
        level[r][c] = '.'
        endscreen(leveldata, level)

    else:  # Empty tile, Laro moves as usual
        level[r][c] = leveldata['standing_on']
        leveldata['standing_on'] = level[r1][c1]
        level[r1][c1] = 'L'
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)

# Edits leveldata to return outcome of pushing a pushable object
def push(level: str, leveldata: dict, tile_to_move: str) -> (str, dict):
    (r, c) = leveldata['laro']
    neighbors = {
        leveldata['control_scheme'][0]: (r-1, c, r-2, c),
        leveldata['control_scheme'][2]: (r+1, c, r+2, c),
        leveldata['control_scheme'][1]: (r, c-1, r, c-2),
        leveldata['control_scheme'][3]: (r, c+1, r, c+2),
    }
    (r1, c1, r2, c2) = neighbors[tile_to_move]  # 1 is the rock, 2 is the tile in front of the rock
    tile_to_push = level[r1][c1]

    if not out_of_borders(r2, c2, leveldata['borders']):
        return (level, leveldata)

    tile_in_front = level[r2][c2]
    if tile_in_front not in {empty, water, paved}:
        return (level, leveldata)  # Doesn't push if the tile the rock is going to is an object
    elif tile_in_front == water:
        level[r][c] = '.'
        level[r1][c1] = 'L'
        if tile_to_push == rock:
            level[r2][c2] = '_'
        leveldata['laro'] = (r1, c1)
        leveldata['paved'] += ((r2, c2),)
        return (level, leveldata)
    else:  # Empty tile; rock can be pushed
        level[r][c] = '.'
        level[r1][c1] = 'L'
        level[r2][c2] = tile_to_push
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)


def pick_up(leveldata: dict) -> dict:
    # Processes picking up items (adding them to laro's inventory and removing the item's coords from leveldata)
    on_top_of = leveldata['standing_on']
    if on_top_of not in items:
        return leveldata
    
    elif on_top_of == axe:
        leveldata['holding'] = 'Axe'

    elif on_top_of == fire:
        leveldata['holding'] = 'Flamethrower'

    elif on_top_of == hammer:
        leveldata['holding'] = 'Hammer'

    leveldata['standing_on'] = empty
    return leveldata


# Applies held item's effects to a target tile (and other tiles i.e. flamethrower)
def use_item(level: str, leveldata: dict, next_tile: tuple) -> (str, dict):
    (r1, c1) = next_tile
    (laro_r, laro_c) = leveldata['laro']
    held_item = leveldata['holding']
    
    if held_item in ('Axe', 'Hammer'):
        pass # Already covered by code below
        
    elif held_item == 'Flamethrower':
        affected_tiles = flamethrower(level, leveldata, r1, c1, frozenset())
        for rx, cx in affected_tiles:
            level[rx][cx] = fire # Convert the tiles to fire for "animation"
        clear()
        print_to_terminal(level)
        sleep(delay*5)
        for rx, cx in affected_tiles:
            level[rx][cx] = empty # Actual tile representation

    # In every item case, the target tile becomes empty and Laro goes to it
    level[r1][c1] = laro
    level[laro_r][laro_c] = empty
                
    leveldata['holding'] = ''
    leveldata['laro'] = (r1, c1)
    return (level, leveldata)

# Used in use_item() to find affected tree tiles into empty tiles
def flamethrower(level: str, leveldata: dict, r: int, c: int, trees: frozenset) -> frozenset:
    neighbors = ((r+1, c), (r-1, c), (r, c+1), (r, c-1))
    level[r][c] = '.'
    valid_neighbors = tuple((rx, cx) for rx, cx in neighbors if out_of_borders(rx, cx, leveldata['borders']))
    tree_neighbors = tuple((rx, cx) for rx, cx in valid_neighbors if level[rx][cx] in flammable)
    if not tree_neighbors:
        return trees
    else:
        return frozenset().union(x for rx, cx in tree_neighbors for x in flamethrower(level, leveldata, rx, cx, frozenset((*trees, (r, c)))))

def out_of_borders(r: int, c: int, borders: tuple) -> bool:
    (rb, cb) = borders
    return not (r >= rb or c >= cb or r < 0 or c < 0)

# Triggered on both win/lose conditions (death, all mushrooms collected)
def endscreen(leveldata: dict, level: str) -> None:
    clear()
    for r, c in leveldata['paved']:
        if level[r][c] == '.':
            level[r][c] = '_'
    level = [''.join(Ui[x] for x in y) for y in level]
    level = '\n'.join(level)
    if len(sys.argv) >= 7:
        write_results(level, leveldata)
        sys.exit()
    print(level)
    is_win = leveldata['mush_collected'] == leveldata['mush_total']
    if is_win:
        letter = input(f'''\

YOU WON!

Game ended in {leveldata['move_count']} move(s)!

Collected {leveldata['mush_collected']} out of {leveldata['mush_total']} mushrooms

PRESS [!] TO RESET
PRESS [Q] TO QUIT
PRESS [Y] TO SUBMIT SCORE

''')
    else:
        letter = input(f'''\
YOU DIED...

Game ended in {leveldata['move_count']} move(s)

Collected {leveldata['mush_collected']} out of {leveldata['mush_total']} mushroom/s

PRESS [!] TO RESET
PRESS [Q] TO QUIT

''')

    if letter.lower() == '!':
        leveldata = {}
        for x in LEVELDATA:
            leveldata[x] = LEVELDATA[x]
        move(LEVEL, leveldata)
    if letter.lower() == 'q':
        clear()
        sys.exit()
    if letter.lower() == 'y' and is_win:
        while True:
            name = input('\nEnter your name (Max of 8 characters): \n')
            if len(name) < 0 or len(name) > 8:
                print('Invalid name')
            else:
                clear()
                print(level + '\n')
                leaderboard(name, leveldata['move_count'])
                while True:
                    letter = input('''\

PRESS [!] TO RESET
PRESS [Q] TO QUIT

''')

                    if letter.lower() == '!':
                        leveldata = {}
                        for x in LEVELDATA:
                            leveldata[x] = LEVELDATA[x]
                        move(LEVEL, leveldata)
                    if letter.lower() == 'q':
                        clear()
                        sys.exit()
                    else:
                        print('Invalid input')


def leaderboard(name: str, score: int) -> None:
    ld_file = f'{sys.argv[2]}_leaderboard.txt' if len(sys.argv) >= 3 else 'demo_level_leaderboard.txt'
    try:
        with open(ld_file, encoding="utf-8") as f:
            leaderboard_raw = f.read()
        if not leaderboard_raw:
            leaderboard = {name: (score, 0)}
        else:
            leaderboard_past = leaderboard_raw.split('\n')
            leaderboard_past = [tuple(ld.split(', ')) for ld in leaderboard_past]
            leaderboard = {n[1:-1]: (int(moves), int(s)) for n, moves, s in leaderboard_past}
            latest_s = max([leaderboard[name][1] for name in leaderboard]) + 1
            leaderboard[name] = (score, latest_s)
    except FileNotFoundError:
        leaderboard = {name: (score, 0)}
    name_order = sort_leaderboard(leaderboard)
    print(f'Score submitted to leaderboard sucessfully. Displaying leaderboard for {LEVEL_NAME}')
    print('''
RANK    NAME            MOVES''')
    names_len = len(name_order)
    names_len = min(10, names_len)
    new_ld = []
    for n in range(names_len):
        n1 = n+1
        sp = ' ' if n1 == 10 else '  '
        nm = name_order[n]
        (moves, s) = leaderboard[nm]
        print(f'{n1}{sp}' + f'     {nm}' + ' '*(8 - len(nm)) + '        ' + f'{moves}')
        current_name = f"'{nm}', {moves}, {s}"
        new_ld.append(current_name)
    new_ld = '\n'.join(new_ld)
    with open(ld_file, 'w', encoding='utf-8') as f:
        f.write(new_ld)


def sort_leaderboard(leaderboard: dict) -> list:
    scores = frozenset(leaderboard[x][0] for x in leaderboard)
    scores = sorted(scores)
    names_in_order = []
    for s in scores:
        score_bracket = [x for x in leaderboard if leaderboard[x][0] == s]
        score_rounds = frozenset(leaderboard[x][1] for x in score_bracket)
        score_rounds = sorted(score_rounds)
        for r in score_rounds:
            for x in score_bracket:
                if leaderboard[x][1] == r:
                    names_in_order.append(x)
                    break
    return names_in_order


#  Special variant of the move command python3 shroom_raider.py -f <stage_file> -m <string_of_moves> -o <output_file>
def move_w_steps(level: str, leveldata: dict, steps: str) -> None:
    levelgrid = level.split('\n')
    levelgrid = [list(x) for x in levelgrid]
    for d in steps:
        clear()
        (laro_r, laro_c) = leveldata['laro']

        for r, c in leveldata['paved']:
            if levelgrid[r][c] == '.':
                levelgrid[r][c] = '_'
        if leveldata['mush_collected'] == leveldata['mush_total']:
            break
        if d.isalpha():
            (laro_r, laro_c) = leveldata['laro']
            if d.upper() in leveldata['control_scheme']:  # Runs if a valid direction is inputted
                (level, leveldata) = move_check(levelgrid, leveldata, d.upper())
            elif d.lower() == 'p':  # Pickup
                if leveldata['standing_on'] and not leveldata['holding']:
                    leveldata = pick_up(leveldata)
            elif d.lower() == 'q':
                raise AssertionError('QUIT GAME')  # Crashes game to avoid going thru recursions
        elif d == '!':  # Fixes bug that retains Laro's position from last run
            leveldata = {}
            for x in LEVELDATA:
                leveldata[x] = LEVELDATA[x]
            levelgrid = LEVEL.split('\n')
            levelgrid = [list(x) for x in levelgrid]
    level = [''.join(x for x in y) for y in levelgrid]
    level = '\n'.join(level)
    write_results(level, leveldata)

# Creates .txt file of the outcome of a game with initial steps in terminal call
def write_results(level: str, leveldata: dict) -> None:
    status = 'CLEAR' if leveldata['mush_collected'] == leveldata['mush_total'] else 'NOT CLEAR'
    with open(sys.argv[6], 'w', encoding='utf-8') as f:
        f.write(status)
        f.write('\n' + level)
        f.write('\n' + f'Collected {leveldata['mush_collected']} out of {leveldata['mush_total']} mushroom/s')
        f.write('\n' + f'Game ended in {leveldata['move_count']} move(s)')


if len(sys.argv) <= 3:
    move(lv, lvd)
else:
    move_w_steps(lv, lvd, sys.argv[4])
