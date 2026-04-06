from panda3d.core import Vec3


class DroneController:
	def __init__(self, root_node, tilt_node, propellers, config, vr_sim):
		self.root = root_node
		self.tilt_node = tilt_node
		self.propellers = propellers
		self.config = config
		self.vr_sim = vr_sim
		self.velocity = Vec3(0, 0, 0)
		self.current_pitch = 0.0
		self.current_roll = 0.0
		self.current_throttle = 0.0
		self.gravity = -22.0
		self.drag_coeff = 0.008
		self.max_tilt = 85.0

	def update(self, dt):
		if dt <= 0.0:
			return

		dt = min(dt, 0.05)

		max_speed = float(self.config.get('max_speed', 15.0))
		acceleration = float(self.config.get('acceleration', 5.0))
		rotation_speed = float(self.config.get('rotation_speed', 90.0))

		throttle_input = self.vr_sim.left_stick.y
		yaw_input = self.vr_sim.left_stick.x
		pitch_input = self.vr_sim.right_stick.y
		roll_input = self.vr_sim.right_stick.x

		throttle_response_speed = acceleration * 2.0
		self.current_throttle += (throttle_input - self.current_throttle) * throttle_response_speed * dt

		self.root.setH(self.root.getH() - yaw_input * rotation_speed * dt)

		target_pitch = -pitch_input * self.max_tilt
		target_roll = roll_input * self.max_tilt

		tilt_speed = 15.0
		self.current_pitch += (target_pitch - self.current_pitch) * tilt_speed * dt
		self.current_roll += (target_roll - self.current_roll) * tilt_speed * dt

		self.tilt_node.setP(self.current_pitch)
		self.tilt_node.setR(self.current_roll)

		parent = self.root.getParent()
		up_vec = parent.getRelativeVector(self.tilt_node, Vec3(0, 0, 1)) if parent else Vec3(0, 0, 1)

		base_thrust = abs(self.gravity)

		if self.current_throttle >= 0:
			active_thrust = base_thrust + (self.current_throttle * max_speed * 5.33)
		else:
			active_thrust = base_thrust * (1.0 + self.current_throttle)

		if self.vr_sim.grip_pressed:
			active_thrust = 0.0

		thrust_force = up_vec * active_thrust

		self.velocity.z += self.gravity * dt
		self.velocity += thrust_force * dt

		speed = self.velocity.length()
		drag_force = self.velocity * speed * self.drag_coeff
		self.velocity -= drag_force * dt

		self.velocity -= self.velocity * 0.4 * dt

		new_pos = self.root.getPos() + self.velocity * dt

		if new_pos.z < 0.2:
			new_pos.z = 0.2
			self.velocity.z = max(0, self.velocity.z)
			self.velocity.x *= 0.5
			self.velocity.y *= 0.5
			self.current_pitch *= 1.0 - 15.0 * dt
			self.current_roll *= 1.0 - 15.0 * dt

		if new_pos.is_nan():
			new_pos = Vec3(0, 0, 5)
			self.velocity = Vec3(0, 0, 0)

		self.root.setPos(new_pos)

		prop_speed = 1500.0 * dt
		if not self.vr_sim.grip_pressed:
			prop_speed += max(0, self.current_throttle) * 7000.0 * dt

		for prop in self.propellers:
			name = prop.getName()
			direction = -1.0 if 'FR' in name or 'BL' in name else 1.0
			prop.setR(prop, prop_speed * direction)
