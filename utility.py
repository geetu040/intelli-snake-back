import json, random, copy
import numpy as np
from keras.models import model_from_json

# GETTING THE MODELS
with open("static/modelling/models/random_model.json", "r") as f:
	random_model = model_from_json(f.read())
random_model.load_weights("static/modelling/models/random_model.h5")

with open("static/modelling/models/fixed_model.json", "r") as f:
	fixed_model = model_from_json(f.read())
fixed_model.load_weights("static/modelling/models/fixed_model.h5")

models = {
	"fixed": fixed_model,
	"random": random_model,
}

# GETTING THE MAP
with open("static/binary_map.json", "r") as f:
	fixed_map = json.loads(f.read())
rows = 31
cols = 28

# FUNCTTIONS FOR AUTOMATION

def automate_faster(info):
	infos = []
	for i in range(info['automated_infos_count']):
		dirs = automate(info, stringify_dirs=False)
		for dir in dirs:
			if move(info, dir): break
			info['second_pref_count'] += 1
			print("SECOND PREFERENCE USED")

		new_info = {}
		for key, value in info.items():
			if key == 'map':
				new_info[key] = value.copy()
			else:
				new_info[key] = value

		infos.append(new_info)
	
	return infos

def move(info, dir):
	h = info['map'].index(3)

	if dir == 0: n = h-cols
	if dir == 1: n = h-1
	if dir == 2: n = h+cols
	if dir == 3: n = h+1

	# IF FOOD IS EATEN
	if (info['map'][n] == 2):
		# updating board
		info['score'] += 1
		info['parts'] += 1
		info['steps'] = 0
		info['map'][n] = info['parts']+3
		# placing food randomly
		if info['map_type'] == 'random':
			info = load_map(info)
			return info
		else:
			info = randomize(info, head=False, food=True)
			
		# r = random.randint(0, 31*28-1)
		# while (info['map'][r] != 0):  r = random.randint(0, 31*28-1)
		# info['map'][r] = 2

	# IF SNAKE HITS THE BODY
	if (info['map'][n] > 4 and info['map'][n] != info['parts']+3 and not info['evade_bite']):
		parts_to_remove = (info['parts']+3) - info['map'][n]
		for i in range(parts_to_remove):
			info['map'][info['map'].index(info['parts']-i+3)] = 0
		info['parts'] -= parts_to_remove
		info['fouls'] += 1

	# MOVING THE BODY
	if ( info['map'][n] != 1 and info['map'][n] != 3 and info['map'][n] != 4 ):
		for i in range(info['parts']+1):
			try:
				cache_n = info['map'].index(3+i)
				info['map'][cache_n] = 0
				info['map'][n] = 3+i
				n = cache_n
			except:
				info['map'][n] = 3+i

		info['steps'] += 1
		if info['steps'] > info['steps_limit']:
			info['steps'] = 0
			info['fouls'] += 1
			# placing food randomly
			info = randomize(info, head=False, food=True)

		return True
	
	return False


def automate(info, stringify_dirs=True):
	x = preprocessing(info['map'], info['map_type'])
	y = models[info['map_type']].predict(x)
	dirs = postprocess(y)
	if stringify_dirs: return str(dirs)
	else: return dirs

def preprocessing(x, type):
	x = np.array(x).reshape(31, 28, 1)
	food_x, food_y = np.where(x == 2)[1], np.where(x == 2)[0]
	head_x, head_y = np.where(x == 3)[1], np.where(x == 3)[0]
	possible_dirs = np.array([[0, 0, 0, 0]])
	try: possible_dirs[0, 0] = int(x[head_y-1, head_x] == 0 or x[head_y-1, head_x] == 2)
	except: pass
	try: possible_dirs[0, 1] = int(x[head_y, head_x-1] == 0 or x[head_y, head_x-1] == 2)
	except: pass
	try: possible_dirs[0, 2] = int(x[head_y+1, head_x] == 0 or x[head_y+1, head_x] == 2)
	except: pass
	try: possible_dirs[0, 3] = int(x[head_y, head_x+1] == 0 or x[head_y, head_x+1] == 2)
	except: pass
		
	possitions = np.array([[head_x[0]/27, head_y[0]/30, food_x[0]/27, food_y[0]/30]])
	if type == 'random':
		maps = np.where(x == 1, 1, 0).reshape(1, 31, 28, 1)
		x = [maps, possitions, possible_dirs]
	elif type == 'fixed':
		x = [possitions, possible_dirs]
	return x

def postprocess(y):
	dirs = [0, 0, 0, 0]
	y = y[0]
	for i in range(4):
		dirs[i] = np.argmax(y)
		y[np.argmax(y)] = -1
	return dirs



# FUNCTIONS FOR MAPS

def load_map(info):
	if info['map_type'] == 'fixed':
		info['map'] = fixed_map[:]
	elif info['map_type'] == 'random':
		info['map'] = [1]*rows*cols
		info['map'] = add_rects(info['map'], times=8, cross=False, d=8)
	info = randomize(info, head=True, food=True)
	return info

def randomize(info, head, food):
	
	if food:
		# finding possition
		r = random.randint(0, rows*cols -1)
		while info['map'][r] != 0:
			r = random.randint(0, rows*cols-1)
		# removing previous
		try: info['map'][info['map'].index(2)] = 0
		except: pass
		# adding new
		info['map'][r] = 2

	if head:
		# removing previous
		for i in range(info['parts']+1):
			try:info['map'][info['map'].index(3+i)] = 0
			except: pass
		# finding possition
		r = random.randint(0, rows*cols -1)
		while info['map'][r] != 0:
			r = random.randint(0, rows*cols-1)
		# adding head
		info['map'][r] = 3
		# adding body
		prev = r
		for part in range(info['parts']):
			dirs = [prev-1, prev+1, prev-cols, prev+cols]
			r = random.choice(dirs)
			while info['map'][r] != 0:
				dirs.remove(r)
				if len(dirs) == 0:
					return randomize(info, head, food)
				r = random.choice(dirs)
			info['map'][r] = 4+part
			prev = r
		if info['map'][info['map'].index(3)+1] != 0 and info['map'][info['map'].index(3)-1] != 0 and info['map'][info['map'].index(3)+cols] != 0 and info['map'][info['map'].index(3)-cols] != 0:
			return randomize(info, head, food)
	return info

def add_rects(map, times=1, d=5, cross=False):
	map = np.array(map).reshape(rows, cols)
	x1, y1 = random.randint(1, cols-2-d), random.randint(1, rows-2-d)
	x2, y2 = random.randint(x1+d, cols-2), random.randint(y1+d, rows-2)

	for x in range(x2-x1+1):
		map[y1, x1+x] = 0
		map[y2, x1+x] = 0
		if cross:
			map[(y1+y2)//2, x1+x] = 0
	for y in range(y2-y1+1):
		map[y1+y, x2] = 0
		map[y1+y, x1] = 0
		if cross:
			map[y1+y, (x1+x2)//2] = 0

	if times == 1: return map.ravel().tolist()
	else: return add_rects(map=map, times=times-1, d=d, cross=cross)

