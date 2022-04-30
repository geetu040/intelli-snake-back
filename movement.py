import numpy as np
from keras.models import model_from_json

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

class Movement():
	def move(self, info):
		if "keyboard_move" in info['message']:
			return self.move_in_dir(dir = info['message'][-1:], info = info)
		elif "food_move" in info['message']:
			return self.move_in_dir(dir = info['message'][-1:], info = info, item=2)
		elif info['message'] == 'move_model':
			x = self.preprocessing(info['map'], info['map_type'])
			y = models[info['map_type']].predict(x)
			dirs = self.postprocess(y)
			if info['allow_second_preference']:
				for i in range(4):
					prev_head = info['map'].index(3)
					info = self.move_in_dir(dir=dirs[i], info=info)
					new_head = info['map'].index(3)
					if prev_head != new_head:
						return info
			# reaches here if models fails to find next step
			return info

	def move_in_dir(self, dir, info, item=3):
		# GETTING THE NEXT STEP
		next_index = info['map'].index(item)
		if dir == 'u':
			if info['map'].index(item) > 27:
				next_index = info['map'].index(item) - self.cols
		elif dir == 'l':
			if info['map'].index(item) % 28 != 0:
				next_index = info['map'].index(item) - 1
		elif dir == 'd':
			if info['map'].index(item) < 840:
				next_index = info['map'].index(item) + self.cols
		elif dir == 'r':
			if info['map'].index(item) % 28 != 27:
				next_index += 1

		# CONDITIONING TO WRITE IN FILE
		if (info['map'][next_index]==0 or info['map'][next_index]==2 or info['map'][next_index]>4):
			self.content += "\n" + str(info['map']) + dir

		# APPLYING CONDITIONS FOR NEXT STEP
		if (info['map'][next_index] == 1 and info['allowcollisions']) or (info['map'][next_index] > 4 and info['map'][next_index]!=max(info['map'])):
			# CHECKING FOR FOULS
			info['fouls'] += 1
		
		if info['map'][next_index] > 4 and info['map'][next_index]!=max(info['map']):
			# CHECKING IF SNAKE ATE ITSELF
			for i in range(info['parts'] + 3 - info['map'][next_index]):
				info['map'][info['map'].index(max(info['map']))] = 0
			info['parts'] -= info['parts'] + 3 - info['map'][next_index]
		
		if info['map'][next_index] == 4:
			# IF SNAKE TRIES TO MOVE BACK
				return info

		if info['map'][next_index] == 1 and not info['allowcollisions']:
			# IF SNAKE HITS THE WALL WITHOUT ALLOWED COLLISION
				return info
		eaten = False #temp
		if (info['map'][next_index] == 2 and item==3):
			# IF FOOD IS EATEN
			info[next_index] = 3
			info['map'] = self.randomize(info['map'], head=False, food=True)
			info[next_index] = 0
			info['score'] += 1
			info['steps'] = 0
			eaten = True # temp
			if info['parts'] < self.maxlen:
				info['parts'] += 1
			

		if (info['map'][next_index] == 0 or info['map'][next_index] == 2 or info['map'][next_index] == max(info['map']) or (info['map'][next_index] == 1 and info['allowcollisions'])) and item==3:
			# MOVING THE SNAKE AND BODY
			for i in range(info['parts']+1):
				try:
					cache_index = info['map'].index(3+i)
				except:
					cache_index = info['map'].index(0)
				info['map'][next_index] = 3+i
				next_index = cache_index
			info['map'][next_index] = 0

		if (info['map'][next_index] == 0 or (info['map'][next_index] == 1 and info['allowcollisions'])) and item==2:
			# MOVING THE FOOD
			cache_index = info['map'].index(2)
			info['map'][next_index] = 2
			info['map'][cache_index] = 0

		# temp while writing
		if eaten and info['allow_writing']:
			map = [1]*self.rows*self.cols
			map = self.add_rects(map, times=8, cross=False, d=8)
			map = self.randomize(map, info['parts'])
			info['map'] = map
			info['map_type'] = 'random'
			info['steps'] = 0

		# for random map changing map after eaten
		if eaten and info['map_type'] == 'random':
			info['message'] = 'random_map'
			info = self.handle_info(info)
			# map = [1]*self.rows*self.cols
			# map = self.add_rects(map, times=8, cross=False, d=8)
			# map = self.randomize(map, info['parts'])
			# info['map'] = map
			# info['steps'] = 0

		return info

	def preprocessing(self, x, type):
		x = np.array(x).reshape(31, 28, 1)
		food_x, food_y = np.where(x == 2)[1], np.where(x == 2)[0]
		head_x, head_y = np.where(x == 3)[1], np.where(x == 3)[0]
		possible_dirs = np.array([[0, 0, 0, 0]])
		try: possible_dirs[0, 0] = int(x[head_y-1, head_x] == 0)
		except: pass
		try: possible_dirs[0, 1] = int(x[head_y, head_x-1] == 0)
		except: pass
		try: possible_dirs[0, 2] = int(x[head_y+1, head_x] == 0)
		except: pass
		try: possible_dirs[0, 3] = int(x[head_y, head_x+1] == 0)
		except: pass
			
		possitions = np.array([[head_x[0]/27, head_y[0]/30, food_x[0]/27, food_y[0]/30]])
		if type == 'random':
			maps = np.where(x == 1, 1, 0).reshape(1, 31, 28, 1)
			x = [maps, possitions, possible_dirs]
		elif type == 'fixed':
			x = [possitions, possible_dirs]
		return x

	def postprocess(self, y):
		dirs = [0, 0, 0, 0]
		y = y[0]
		for i in range(4):
			dirs[i] = np.argmax(y)
			y[np.argmax(y)] = -1
		dirs = list(map(
			lambda x: ['u', 'l', 'd', 'r'][x],
			dirs
		))
		return dirs