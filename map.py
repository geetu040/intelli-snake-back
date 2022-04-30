import json, random
from movement import Movement
import numpy as np

class Map(Movement):
	def __init__(self, rows, cols, fixed_map_url):
		with open(fixed_map_url, "r") as f:
			self.fixed_map = json.loads(f.read())
		self.rows = rows
		self.cols = cols
		self.maxlen = 100
		self.content = ''
		self.max_steps = 100

	def handle_info(self, info):
		if info['message'] == 'fixed_map':
			map = self.fixed_map[:]
			map = self.randomize(map, info['parts'])
			info['map'] = map
			info['map_type'] = 'fixed'
			info['steps'] = 0

		elif info['message'] == 'random_map':
			map = [1]*self.rows*self.cols
			map = self.add_rects(map, times=8, cross=False, d=8)
			map = self.randomize(map, info['parts'])
			info['map'] = map
			info['map_type'] = 'random'
			info['steps'] = 0

		elif 'move' in info['message']:

			info = self.move(info)
			info['steps'] += 1
			if info['steps'] > self.max_steps and info['message'] == 'move_model':
				info['map'] = self.randomize(info['map'], head=False, food=True)
				info['steps'] = 0
				info['fouls'] += 1
			

		elif info['message'] == 'replace_food':
			info['map'] = self.randomize(info['map'], parts=None, head=False, food=True)
			info['steps'] = 0

		elif info['message'] == 'replace_snake':
			info['map'] = self.randomize(info['map'], parts=info['parts'], head=True, food=False)
			info['steps'] = 0

		# WRITING INTO FILE
		elif info['message'] == 'write':
			with open("latest_dataset.txt", "a") as f:
				f.write(self.content)
				self.content = ''
		elif info['message'] == 'clean':
			self.content = ''

		return info

	def randomize(self, map, parts=None, head=True, food=True):
		if food:
			try:
				map[map.index(2)] = 0
			except:
				pass
			i = random.randint(0, self.rows * self.cols -1)
			while map[i] != 0:
				i = random.randint(0, self.rows * self.cols -1)
			map[i] = 2
		if head:
			try:
				for i in range(parts+1):
					map[map.index(3+i)] = 0
			except:
				pass
			i = random.randint(0, self.rows * self.cols -1)
			while map[i] != 0:
				i = random.randint(0, self.rows * self.cols -1)
			map[i] = 3
			# GETTING THE BODY
			step = i
			for j in range(parts):
				iterations = 0
				while True:
					iterations += 1
					if iterations > 30:
						return self.randomize(map, parts, head, food)
					body_dir = random.randint(0, 3)
					if body_dir == 0 and map[step-self.cols] == 0:
						map[step-self.cols] = j+4
						step = step-self.cols
						break
					elif body_dir == 1 and map[step-1] == 0:
						map[step-1] = j+4
						step = step-1
						break
					elif body_dir == 2 and map[step+self.cols] == 0:
						map[step+self.cols] = j+4
						step = step+self.cols
						break
					elif body_dir == 3 and map[step+1] == 0:
						map[step+1] = j+4
						step = step+1
						break
			if map[map.index(3)+1] != 0 and map[map.index(3)-1] != 0 and map[map.index(3)+self.cols] != 0 and map[map.index(3)-self.cols] != 0:
				return self.randomize(map, parts, head, food)
		return map

	def add_rects(self, map, times=1, d=5, cross=False):
		map = np.array(map).reshape(31, 28)
		x1, y1 = random.randint(1, self.cols-2-d), random.randint(1, self.rows-2-d)
		x2, y2 = random.randint(x1+d, self.cols-2), random.randint(y1+d, self.rows-2)

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
		else: return self.add_rects(map=map, times=times-1, d=d, cross=cross)


			
		

