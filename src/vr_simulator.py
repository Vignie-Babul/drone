from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3, WindowProperties

class VRSimulator(DirectObject):
	def __init__(self, base):
		self.base = base
		self.left_stick = Vec3(0, 0, 0)
		self.right_stick = Vec3(0, 0, 0)
		self.trigger_pressed = False
		self.grip_pressed = False
		props = WindowProperties()
		props.setCursorHidden(True)
		props.setMouseMode(WindowProperties.M_relative)
		self.base.win.requestProperties(props)
		bindings = [
			('w', 'left', 'y', 1),
			('w-up', 'left', 'y', 0),
			('s', 'left', 'y', -1),
			('s-up', 'left', 'y', 0),
			('a', 'left', 'x', -1),
			('a-up', 'left', 'x', 0),
			('d', 'left', 'x', 1),
			('d-up', 'left', 'x', 0),
			('arrow_up', 'right', 'y', 1),
			('arrow_up-up', 'right', 'y', 0),
			('arrow_down', 'right', 'y', -1),
			('arrow_down-up', 'right', 'y', 0),
			('arrow_left', 'right', 'x', -1),
			('arrow_left-up', 'right', 'x', 0),
			('arrow_right', 'right', 'x', 1),
			('arrow_right-up', 'right', 'x', 0),
		]
		for key, stick, axis, val in bindings:
			self.accept(key, self.set_stick, [stick, axis, val])
		self.accept('space', self.set_trigger, [True])
		self.accept('space-up', self.set_trigger, [False])
		self.accept('shift', self.set_grip, [True])
		self.accept('shift-up', self.set_grip, [False])

	def set_stick(self, stick, axis, val):
		if stick == 'left':
			if axis == 'y':
				self.left_stick.y = val
			if axis == 'x':
				self.left_stick.x = val
		elif stick == 'right':
			if axis == 'y':
				self.right_stick.y = val
			if axis == 'x':
				self.right_stick.x = val

	def set_trigger(self, state):
		self.trigger_pressed = state

	def set_grip(self, state):
		self.grip_pressed = state
