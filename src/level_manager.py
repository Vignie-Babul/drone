import math
import random
from panda3d.core import NodePath, Vec3


class LevelManager:
	def __init__(self, app):
		self.app = app
		self.rings = []
		self.obstacles = []
		self.moving_obstacles = []
		self.score = 0
		self.finished = False
		self.snd_collect = self.app.loader.loadSfx('src/assets/sounds/collect-point.mp3')
		self.snd_hit = self.app.loader.loadSfx('src/assets/sounds/hard-punch.mp3')
		self.snd_finish = self.app.loader.loadSfx('src/assets/sounds/finish.mp3')
		self.build_level()

	def build_level(self):
		for i in range(12):
			y = 20 + i * 25
			self.create_ring(Vec3(0, y, 10))
		for i in range(15):
			y = 30 + i * 20
			x = random.uniform(-15, 15)
			self.create_obstacle(Vec3(x, y, random.uniform(5, 15)), i % 3)
		finish_pos = Vec3(0, 350, 10)
		self.create_finish(finish_pos)

	def create_ring(self, pos):
		ring_root = NodePath('ring')
		ring_root.setPos(pos)
		dims = [(-3.0, 0, 0.5, 6), (3.0, 0, 0.5, 6), (0, 3.0, 6.5, 0.5), (0, -3.0, 6.5, 0.5)]
		for dx, dz, sx, sz in dims:
			side = self.app.loader.loadModel('box')
			side.setScale(sx, 0.5, sz)
			side.setPos(dx, 0, dz)
			side.setColor(1, 1, 0, 1)
			side.reparentTo(ring_root)
		ring_root.reparentTo(self.app.render)
		self.rings.append(ring_root)

	def create_obstacle(self, pos, obs_type):
		obs = self.app.loader.loadModel('box')
		obs.setPos(pos)
		if obs_type == 0:
			obs.setScale(4, 1, 6)
			obs.setColor(0.8, 0.2, 0.2, 1)
		elif obs_type == 1:
			obs.setScale(2, 2, 15)
			obs.setColor(0.2, 0.8, 0.2, 1)
		else:
			obs.setScale(3, 3, 3)
			obs.setColor(0.2, 0.2, 0.8, 1)
			self.moving_obstacles.append({'node': obs, 'start_x': pos.x, 'time': random.uniform(0, 10)})
		obs.reparentTo(self.app.render)
		self.obstacles.append(obs)

	def create_finish(self, pos):
		self.finish_node = self.app.loader.loadModel('box')
		self.finish_node.setScale(10, 1, 10)
		self.finish_node.setPos(pos)
		self.finish_node.setColor(1, 1, 1, 0.5)
		self.finish_node.reparentTo(self.app.render)

	def reset(self):
		for ring in self.rings:
			ring.removeNode()
		for obs in self.obstacles:
			obs.removeNode()
		if hasattr(self, 'finish_node'):
			self.finish_node.removeNode()
		self.rings.clear()
		self.obstacles.clear()
		self.moving_obstacles.clear()
		self.score = 0
		self.finished = False
		self.build_level()

	def update(self, dt, drone_pos):
		for mo in self.moving_obstacles:
			mo['time'] += dt
			mo['node'].setX(mo['start_x'] + math.sin(mo['time']) * 15)
		for ring in self.rings[:]:
			if (drone_pos - ring.getPos()).length() < 6.5:
				self.score += 100
				self.snd_collect.play()
				ring.removeNode()
				self.rings.remove(ring)
		for obs in self.obstacles:
			if (drone_pos - obs.getPos()).length() < 4.5:
				penalty = self.app.drone_config.get('obstacle_penalty', 50)
				self.score -= penalty
				self.snd_hit.play()
				self.app.drone_ctrl.bounce_back()

	def check_finish(self, drone_pos):
		if not self.finished and drone_pos.y >= 350.0:
			self.finished = True
			self.snd_finish.play()
			return True
		return False
