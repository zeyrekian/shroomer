LEVEL = '''\
TTTTTTTTTTT
T...T+T...T
T.*.T~T.x.T
T.TT.~....T
T.TxTL.*..T
T.TTT.....T
T..R...R..T
T.........T
TTTTTTTTTTT
'''

LEVELDATA = { 
# Contains important data such as coords of Laro and other items
# Will eventually make a command to automatically make leveldata with only the level
	'borders': (9, 11),
	'laro': (4, 5),
	'mushrooms': (),
	'mush_count': (),
	'paved': (),
	'axe': [(4, 3), (2, 8)],
	'fire': [(4, 7), (2, 2)],
	'standing_on': '',
	'holding': '',

}

lv = LEVEL

lvd = {}
for x in LEVELDATA:
	lvd[x] = LEVELDATA[x]




def move(level, leveldata): 
# Gets your next input, runs a different command according to your input
	(laro_r, laro_c) = leveldata['laro']
	levelgrid = level.split('\n')
	levelgrid = [list(x) for x in levelgrid]
	if (laro_r, laro_c) in leveldata['axe']: leveldata['standing_on'] = 'Axe'
	elif (laro_r, laro_c) in leveldata['fire']: leveldata['standing_on'] = 'Flamethrower'
	else: leveldata['standing_on'] = ''
	print('\n' + level)
	direction = input(f'''\
[W] = UP
[A] = LEFT
[S] = DOWN
[D] = RIGHT

[P] = PICK UP
[!] = RESET
[Q] = EXIT

Currently standing on: {leveldata['standing_on']}
You currently have: {leveldata['holding']}

Choose your next move: ''') 
	if direction in ('w', 'W', 'a', 'A', 's', 'S', 'd', 'D'): # Runs if a valid direction is inputted
		(level, leveldata) = move_check(levelgrid, leveldata, direction.lower())
		for r, c in leveldata['paved']:
			if level[r][c] == '.': level[r][c] = '_'
		for r, c in leveldata['axe']:
			if level[r][c] == '.': level[r][c] = 'x'
		for r, c in leveldata['fire']:
			if level[r][c] == '.': level[r][c] = '*'
		level = [''.join(x for x in y) for y in levelgrid]
		level = '\n'.join(level)
		move(level, leveldata)
	elif direction.lower() == 'p': # Pickup
		if leveldata['standing_on'] and not leveldata['holding']: leveldata = pick_up(leveldata)
		move(level, leveldata)
	elif direction.lower() == 'q' : raise AssertionError('QUIT GAME') # Crashes game to avoid going thru recursions
	elif direction.lower() == '!' : # Fixes bug that retains Laro's position from last run
		leveldata = {}
		for x in LEVELDATA:
			leveldata[x] = LEVELDATA[x]
		move(LEVEL, leveldata)

def move_check(level, leveldata, tile_to_move): 
# Checks the tile Laro is about to move into, runs different commands depending on what laro runs into
	(r, c) = leveldata['laro']
	neighbors = {
		'w': (r-1, c),
		's': (r+1, c),
		'a': (r, c-1),
		'd': (r, c+1),
	}
	(r1, c1) = neighbors[tile_to_move] # Tile Laro is about to move to, used to check what kind of tile laro is about to run to
	if level[r1][c1] == 'T': 
		if leveldata['holding']: return use_item(level, leveldata, (r1, c1)) # Runs in case Laro has an item
		else: return (level, leveldata) # Returns same level state, laro doesnt move (if Laro has no item)
	elif level[r1][c1] == 'R': return move_rock(level, leveldata, tile_to_move) # Runs rock pushing command
	elif level[r1][c1] == '~': # Laro dies
		deathscreen()
	else: # If tile is empty, laro moves as usual 
		level[r][c] = '.'
		level[r1][c1] = 'L'
		leveldata['laro'] = (r1, c1)
		return (level, leveldata)

def move_rock(level, leveldata, tile_to_move): 
# Runs if you run into a rock to push it
	(r, c) = leveldata['laro'] 
	neighbors = {
		'w': (r-1, c, r-2, c),
		's': (r+1, c, r+2, c),
		'a': (r, c-1, r, c-2),
		'd': (r, c+1, r, c+2),
	}
	(r1, c1, r2, c2) = neighbors[tile_to_move] # 1 is the rock, 2 is the tile in front of the rock
	if level[r2][c2] in ('T', 'R', 'x', '*'): return (level, leveldata) # Doesn't push if the tile the rock is going to is an object
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
		flame = flamethrower(level, leveldata, r1, c1, frozenset())
		print(flame)
		for rx, cx in flame:
			level[rx][cx] = '.'
	leveldata['holding'] = ''
	return (level, leveldata)

def flamethrower(level, leveldata, r, c, trees):
# NOT DONE YET, WILL FIX SOON
	trees = frozenset((*trees, (r, c)))
	neighbors = ((r+1, c), (r-1, c), (r, c+1), (r, c-1))
	level[r][c] = '.'
	valid_neighbors = tuple((rx, cx) for rx, cx in neighbors if out_of_borders(rx, cx, leveldata['borders']))
	tree_neighbors = tuple((rx, cx) for rx, cx in valid_neighbors if level[rx][cx] == 'T')
	if not tree_neighbors: return trees
	else: return trees.union(flamethrower(level, leveldata, rx, cx, trees) for rx, cx in tree_neighbors)
		
def out_of_borders(r, c, borders):
	(rb, cb) = borders
	if r >= rb or c >= cb or r < 0 or c < 0: return False
	else: return True


def deathscreen(): 
# Runs when Laro runs into water and drowns lmao
	letter = input('''\


YOU DIED...

PRESS [!] TO RESET
PRESS [Q] TO QUIT

''')

	if letter.lower() == '!': 
		leveldata = {}
		for x in LEVELDATA:
			leveldata[x] = LEVELDATA[x]
		move(LEVEL, leveldata)
	if letter.lower() == 'q': raise AssertionError('QUIT GAME')


move(lv, lvd)