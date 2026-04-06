import random
from panda3d.core import Vec3

class VFXManager:
	def __init__(self, app):
		self.app = app
		self.particles = []

	def spawn(self, pos, count, color, speed_base, gravity=-9.8, life=1.0, size=0.2):
		for _ in range(int(count)):
			p = self.app.loader.loadModel('box')
			p.setScale(size)
			p.setColor(*color)
			p.setPos(pos)
			p.setTransparency(1)
			p.reparentTo(self.app.render)
			vel = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
			vel.normalize()
			vel *= speed_base * random.uniform(0.5, 1.5)
			self.particles.append({'node': p, 'vel': vel, 'life': life, 'max_life': life, 'gravity': gravity})

	def spawn_ground_impact(self, pos, force):
		count = min(int(force * 5), 50)
		self.spawn(pos, count, (0.4, 0.3, 0.1, 1.0), force * 0.8, -5.0, 0.6, 0.1)

	def spawn_ring_pass(self, pos):
		self.spawn(pos, 40, (1.0, 1.0, 0.2, 1.0), 12.0, 0.0, 1.2, 0.15)

	def spawn_collision(self, pos, force):
		count = min(int(force * 4), 100)
		self.spawn(pos, count, (1.0, 0.3, 0.1, 1.0), force * 1.5, -9.8, 0.8, 0.25)

	def spawn_finish(self, pos):
		self.spawn(pos, 250, (0.2, 1.0, 0.4, 1.0), 30.0, -4.0, 3.0, 0.3)

	def update(self, dt):
		active = []
		for p in self.particles:
			p['life'] -= dt
			if p['life'] <= 0:
				p['node'].removeNode()
			else:
				p['vel'].z += p['gravity'] * dt
				p['node'].setPos(p['node'].getPos() + p['vel'] * dt)
				alpha = p['life'] / p['max_life']
				c = p['node'].getColor()
				p['node'].setColor(c[0], c[1], c[2], alpha)
				active.append(p)
		self.particles = active
