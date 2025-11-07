import os

import sys

LEVEL = ''

def main():
# Checks if there is a level inputted along with the command, loads the demo if there is no level 
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], encoding='utf-8') as f:
                return (f.read())
        except FileNotFoundError: 
            print('Level file not found')
            exit()
    else: 
        return '''\
TTTTTTTTTTT
T...T+T...T
T.*.T~T.x.T
T.TT.~....T
T.T+TL.*..T
T.TTT.....T
T..R...R~~T
T.......~+T
TTTTTTTTTTT'''

LEVEL = main()

# LEVELDATA
# Contains important data such as coords of Laro and other items
winners = {}
def create_leveldata(level):
# Reads the level and makes leveldata
    result = {
    'borders': (0, 0),
    'laro': (0, 0),
    'mush_collected': 0,
    'mush_total': 0,
    'paved': (),
    'axe': [],
    'fire': [],
    'standing_on': '',
    'holding': '',
    'move_count': 0,
    'control_scheme': (),
    }
    levelgrid = level.split('\n')
    (r, c) = (len(levelgrid), len(levelgrid[0]))
    result['borders'] = (r, c)
    for i in range(r):
        for j in range(c):
            if levelgrid[i][j] == '*': result['fire'].append((i, j))
            elif levelgrid[i][j] == 'x': result['axe'].append((i, j))
            elif levelgrid[i][j] == '+': result['mush_total'] += 1
            elif levelgrid[i][j] == 'L': result['laro'] =  (i, j)   
    control_scheme_choice = {
    'w': ('W', 'A', 'S', 'D'),
    'u': ('U', 'L', 'D', 'R')
    }
    os.system('clear')
    while True:
        with open("menu.txt", encoding='utf-8') as m:
            choice = input(m.read())
        if choice in ('w', 'W', 'u', 'U'): 
            result['control_scheme'] = control_scheme_choice[choice.lower()]
            break
        elif choice.lower() == "q":
            quit()
        else: print('Invalid input. Try again') 
    return result

LEVELDATA = create_leveldata(LEVEL)

lv = LEVEL

lvd = {}
for x in LEVELDATA:
    lvd[x] = LEVELDATA[x]


def move(level, leveldata): 
    levelgrid = level.split('\n')
    levelgrid = [list(x) for x in levelgrid]
    while True:
        os.system('clear')
        (laro_r, laro_c) = leveldata['laro']
        if (laro_r, laro_c) in leveldata['axe']: leveldata['standing_on'] = 'Axe'
        elif (laro_r, laro_c) in leveldata['fire']: leveldata['standing_on'] = 'Flamethrower'
        else: leveldata['standing_on'] = ''
        for r, c in leveldata['paved']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = '_'
        for r, c in leveldata['axe']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = 'x'
        for r, c in leveldata['fire']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = '*'
        level = [''.join(x for x in y) for y in levelgrid]
        level = '\n'.join(level)
        if leveldata['mush_collected'] == leveldata['mush_total']: endscreen(leveldata, levelgrid)
        print(level + '\n')
        direction = input(f'''\
[{leveldata['control_scheme'][0]}] = UP
[{leveldata['control_scheme'][1]}] = LEFT
[{leveldata['control_scheme'][2]}] = DOWN
[{leveldata['control_scheme'][3]}] = RIGHT

[P] = PICK UP
[!] = RESET
[Q] = EXIT

Collected {leveldata['mush_collected']} out of {leveldata['mush_total']} mushrooms

Currently standing on: {leveldata['standing_on']}
You currently have: {leveldata['holding']}

Choose your next move: ''') 
        for d in direction:
            if d.isalpha():
                (laro_r, laro_c) = leveldata['laro']
                if (laro_r, laro_c) in leveldata['axe']: leveldata['standing_on'] = 'Axe'
                elif (laro_r, laro_c) in leveldata['fire']: leveldata['standing_on'] = 'Flamethrower'
                if d.upper() in leveldata['control_scheme']: # Runs if a valid direction is inputted
                    (level, leveldata) = move_check(levelgrid, leveldata, d.upper())
                elif d.lower() == 'p': # Pickup
                    if leveldata['standing_on'] and not leveldata['holding']: leveldata = pick_up(leveldata)
                elif d.lower() == 'q' : exit()
            elif d == '!' : # Fixes bug that retains Laro's position from last run
                leveldata = {}
                for x in LEVELDATA:
                    leveldata[x] = LEVELDATA[x]
                levelgrid = LEVEL.split('\n')
                levelgrid = [list(x) for x in levelgrid]

def move_check(level, leveldata, tile_to_move): 
# Checks the tile Laro is about to move into, runs different commands depending on what laro runs into
    leveldata['move_count'] += 1
    (r, c) = leveldata['laro']
    neighbors = {
        leveldata['control_scheme'][0]: (r-1, c),
        leveldata['control_scheme'][2]: (r+1, c),
        leveldata['control_scheme'][1]: (r, c-1),
        leveldata['control_scheme'][3]: (r, c+1),
    }
    (r1, c1) = neighbors[tile_to_move] # Tile Laro is about to move to, used to check what kind of tile laro is about to run to
    if not out_of_borders(r1, c1, leveldata['borders']):return (level, leveldata)
    elif level[r1][c1] == 'T': 
        if leveldata['holding']: return use_item(level, leveldata, (r1, c1)) # Runs in case Laro has an item
        else: return (level, leveldata) # Returns same level state, laro doesnt move (if Laro has no item)
    elif level[r1][c1] == 'R': return move_rock(level, leveldata, tile_to_move) # Runs rock pushing command
    elif level[r1][c1] == '+':
        leveldata['mush_collected'] += 1
        level[r][c] = '.'
        level[r1][c1] = 'L'
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)
    elif level[r1][c1] == '~': # Laro dies
        level[r][c] = '.'
        endscreen(leveldata, level)
    else: # If tile is empty, laro moves as usual 
        level[r][c] = '.'
        level[r1][c1] = 'L'
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)

def move_rock(level, leveldata, tile_to_move): 
# Runs if you run into a rock to push it
    (r, c) = leveldata['laro'] 
    neighbors = {
        leveldata['control_scheme'][0]: (r-1, c, r-2, c),
        leveldata['control_scheme'][2]: (r+1, c, r+2, c),
        leveldata['control_scheme'][1]: (r, c-1, r, c-2),
        leveldata['control_scheme'][3]: (r, c+1, r, c+2),
    }
    (r1, c1, r2, c2) = neighbors[tile_to_move] # 1 is the rock, 2 is the tile in front of the rock
    if not out_of_borders(r2, c2, leveldata['borders']): return (level, leveldata)
    if level[r2][c2] in ('T', 'R', 'x', '*', '+'): return (level, leveldata) # Doesn't push if the tile the rock is going to is an object
    elif level[r2][c2] == '~':
        level[r][c] = '.'
        level[r1][c1] = 'L'
        level[r2][c2] = '_'
        leveldata['laro'] = (r1, c1)
        leveldata['paved'] = leveldata['paved'] + ((r2, c2),)
        return (level, leveldata)
    else:
        level[r][c] = '.'
        level[r1][c1] = 'L'
        level[r2][c2] = 'R'
        leveldata['laro'] = (r1, c1)
        return (level, leveldata)

def pick_up(leveldata): 
# Processes picking up items (adding them to laro's inventory and removing the item's coords from leveldata)
    if leveldata['standing_on'] == 'Axe':
        leveldata['holding'] = 'Axe'
        leveldata['axe'] = [x for x in leveldata['axe'] if x != leveldata['laro']]
    elif leveldata['standing_on'] == 'Flamethrower':
        leveldata['holding'] = 'Flamethrower'
        leveldata['fire'] = [x for x in leveldata['fire'] if x != leveldata['laro']]
    return leveldata

def use_item(level, leveldata, next_tile):
    (r1, c1) = next_tile
    if leveldata['holding'] == 'Axe': level[r1][c1] = '.'
    elif leveldata['holding'] == 'Flamethrower': 
        for rx, cx in flamethrower(level, leveldata, r1, c1, frozenset()):
            level[rx][cx] = '.'
    leveldata['holding'] = ''
    return (level, leveldata)

def flamethrower(level, leveldata, r, c, trees):
# FIXED, returns a frozenset of coords of all trees adjacent to (r, c)
    neighbors = ((r+1, c), (r-1, c), (r, c+1), (r, c-1))
    level[r][c] = '.'
    valid_neighbors = tuple((rx, cx) for rx, cx in neighbors if out_of_borders(rx, cx, leveldata['borders']))
    tree_neighbors = tuple((rx, cx) for rx, cx in valid_neighbors if level[rx][cx] == 'T')
    if not tree_neighbors: return trees
    else: return frozenset().union(x for rx, cx in tree_neighbors for x in flamethrower(level, leveldata, rx, cx, frozenset((*trees, (r, c)))))
        
def out_of_borders(r, c, borders):
    (rb, cb) = borders
    if r >= rb or c >= cb or r < 0 or c < 0: return False
    else: return True


def endscreen(leveldata, level): 
# Runs when you encounter an end state (laro dies or you collect all mushies)
# Also appears the board state after the game ends
    os.system('clear')
    for r, c in leveldata['paved']:
        if level[r][c] == '.': level[r][c] = '_'
    for r, c in leveldata['axe']:
        if level[r][c] == '.': level[r][c] = 'x'
    for r, c in leveldata['fire']:
        if level[r][c] == '.': level[r][c] = '*'
    level = [''.join(x for x in y) for y in level]
    level = '\n'.join(level)
    if len(sys.argv) >= 7: 
        write_results(level, leveldata)
        quit()
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
    else: letter = input(f'''\
YOU DIED...

Game ended in {leveldata['move_count']} move(s)

Collected {leveldata['mush_collected']} out of {leveldata['mush_total']} mushrooms

PRESS [!] TO RESET
PRESS [Q] TO QUIT

''')

    if letter.lower() == '!': 
        leveldata = {}
        for x in LEVELDATA:
            leveldata[x] = LEVELDATA[x]
        move(LEVEL, leveldata)
    if letter.lower() == 'q': quit()
    if letter.lower() == 'y' and is_win: 
        name = input("Enter your Name:")

def leaderboard(name,leveldata):
    winners

def move_w_steps(level, leveldata, steps): 
# special variant of the move command that is accessed when the format of the command is python3 shroom_raider.py -f <stage_file> -m <string_of_moves> -o <output_file>
    levelgrid = level.split('\n')
    levelgrid = [list(x) for x in levelgrid]
    for d in steps:
        os.system('clear')
        (laro_r, laro_c) = leveldata['laro']
        if (laro_r, laro_c) in leveldata['axe']: leveldata['standing_on'] = 'Axe'
        elif (laro_r, laro_c) in leveldata['fire']: leveldata['standing_on'] = 'Flamethrower'
        else: leveldata['standing_on'] = ''
        for r, c in leveldata['paved']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = '_'
        for r, c in leveldata['axe']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = 'x'
        for r, c in leveldata['fire']:
            if levelgrid[r][c] == '.': levelgrid[r][c] = '*'
        if leveldata['mush_collected'] == leveldata['mush_total']: break
        if d.isalpha():
            (laro_r, laro_c) = leveldata['laro']
            if (laro_r, laro_c) in leveldata['axe']: leveldata['standing_on'] = 'Axe'
            elif (laro_r, laro_c) in leveldata['fire']: leveldata['standing_on'] = 'Flamethrower'
            if d.upper() in leveldata['control_scheme']: # Runs if a valid direction is inputted
                (level, leveldata) = move_check(levelgrid, leveldata, d.upper())
            elif d.lower() == 'p': # Pickup
                if leveldata['standing_on'] and not leveldata['holding']: leveldata = pick_up(leveldata)
            elif d.lower() == 'q' : raise AssertionError('QUIT GAME') # Crashes game to avoid going thru recursions
        elif d == '!' : # Fixes bug that retains Laro's position from last run
            leveldata = {}
            for x in LEVELDATA:
                leveldata[x] = LEVELDATA[x]
            levelgrid = LEVEL.split('\n')
            levelgrid = [list(x) for x in levelgrid]
    level = [''.join(x for x in y) for y in levelgrid]
    level = '\n'.join(level)
    write_results(level, leveldata)

def write_results(level, leveldata):
# Writes the results in the output file
    if leveldata['mush_collected'] == leveldata['mush_total']: status = 'CLEAR'
    else: status = 'NOT CLEAR'
    with open(sys.argv[6], 'w', encoding='utf-8') as f:
        f.write(status)
        f.write('\n' + level)
        f.write('\n' + f'Game ended in {leveldata['move_count']} move(s)')

if len(sys.argv) <= 3: move(lv, lvd)
else: move_w_steps(lv, lvd, sys.argv[4])

# Try entering the command below with this code and the level1 here, should create a .py file saying CLEAR
# python3 -m shroomraider2 -f level1.py -m awadwadwadwaaasssssss -o result.py
