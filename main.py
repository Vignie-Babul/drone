import atexit
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, NodePath, Vec3, ClockObject, WindowProperties, loadPrcFileData

loadPrcFileData('', 'notify-level-ffmpeg error')
loadPrcFileData('', 'window-resizeable true')

from src.config import PATHS, JSONConfig, Localization, SlotJSONConfig, UI_TEXT
from src.data import DataSave, Analytics
from src.vr_simulator import VRSimulator
from src.drone_controller import DroneController
from src.ui import UIManager
from src.level_manager import LevelManager
from src.utils import get_iso_datetime
from src.vfx import VFXManager

class VRDroneSimulatorApp(ShowBase):
	def __init__(self):
		super().__init__()
		self.disableMouse()
		self.game_started_time = get_iso_datetime()
		self.analytics = Analytics(PATHS['data']['analytics'])
		self.last_attempt_data = "No attempts made"
		self.last_attempt_status = False
		self.settings = JSONConfig(PATHS['conf']['settings'])
		self.local = Localization(
			PATHS['conf']['local'],
			UI_TEXT,
			self.settings,
		)
		self.drone_config_manager = SlotJSONConfig(
			PATHS['conf']['drone'],
			{
				'max_speed': 15.0,
				'acceleration': 5.0,
				'rotation_speed': 90.0,
				'battery_life': 300.0,
				'obstacle_penalty': 50,
			},
			self.settings,
		)
		self.drone_config = self.drone_config_manager.load()
		self.data_save = DataSave(PATHS['data']['save'], self.settings)
		self.setup_scene()
		self.setup_drone()
		self.vfx = VFXManager(self)
		self.vr_sim = VRSimulator(self)
		self.drone_ctrl = DroneController(
			self.drone_root, self.drone_tilt, self.propellers, self.drone_config, self.vr_sim
		)
		self.level_manager = LevelManager(self)
		self.ui_manager = UIManager(self)
		self.battery = float(self.drone_config.get('battery_life', 300.0))
		self.run_time = 0.0
		self.total_distance = 0.0
		self.max_speed_run = 0.0
		self.vr_enabled = False
		try:
			from panda3d_openxr import OpenXRBase
			self.xr = OpenXRBase()
			self.xr.create()
			self.vr_enabled = True
		except ImportError:
			pass
		
		if self.vr_enabled:
			self.cam_anchor.reparentTo(self.drone_tilt)
			self.cam_anchor.setPosHpr(0, 0, 0, 0, 0, 0)
			self.drone_model.hide()

		self.taskMgr.add(self.update_loop, 'update_loop')
		self.accept('f', self.toggle_fullscreen)
		atexit.register(self.send_session_analytics)

	def toggle_fullscreen(self):
		props = WindowProperties()
		props.setFullscreen(not self.win.getProperties().getFullscreen())
		self.win.requestProperties(props)

	def setup_scene(self):
		alight = AmbientLight('alight')
		alight.setColor((0.6, 0.6, 0.6, 1))
		alnp = self.render.attachNewNode(alight)
		self.render.setLight(alnp)
		dlight = DirectionalLight('dlight')
		dlight.setColor((0.8, 0.8, 0.8, 1))
		dlnp = self.render.attachNewNode(dlight)
		dlnp.setHpr(45, -45, 0)
		self.render.setLight(dlnp)
		self.ground = self.loader.loadModel('box')
		self.ground.setScale(1000, 1000, 1)
		self.ground.setPos(-500, -200, -1)
		self.ground.setColor(0.2, 0.6, 0.2, 1)
		self.ground.reparentTo(self.render)

	def setup_drone(self):
		self.drone_root = NodePath('drone_root')
		self.drone_root.reparentTo(self.render)
		self.drone_root.setPos(0, 0, 5)
		self.drone_tilt = NodePath('drone_tilt')
		self.drone_tilt.reparentTo(self.drone_root)
		try:
			self.drone_model = self.loader.loadModel('src/assets/models/fpv_drone.glb')
			self.drone_model.setScale(0.01)
			self.drone_model.setHpr(90, 0, 0)
			self.propellers = self.drone_model.findAllMatches('**/prop_*')
		except Exception:
			self.drone_model = self.loader.loadModel('box')
			self.drone_model.setScale(0.5)
			self.propellers = []
		self.drone_model.reparentTo(self.drone_tilt)
		
		self.cam_target = NodePath('cam_target')
		self.cam_target.reparentTo(self.drone_root)
		self.cam_target.setPos(0, -6, 2.5)
		
		self.cam_anchor = NodePath('cam_anchor')
		self.cam_anchor.reparentTo(self.render)
		
		self.camera.reparentTo(self.cam_anchor)
		self.camera.setPosHpr(0, 0, 0, 0, 0, 0)
		
		self.cam_anchor.setPos(self.cam_target.getPos(self.render))
		self.cam_anchor.lookAt(self.drone_root.getPos() + Vec3(0, 0, 1.0))

	def update_loop(self, task):
		if hasattr(self, 'ui_manager') and self.ui_manager.state != 'GAME':
			if (
				hasattr(self, 'drone_ctrl')
				and self.drone_ctrl.engine_sound.status() == self.drone_ctrl.engine_sound.PLAYING
			):
				self.drone_ctrl.engine_sound.stop()
			return task.cont
		else:
			if (
				hasattr(self, 'drone_ctrl')
				and self.drone_ctrl.engine_sound.status() != self.drone_ctrl.engine_sound.PLAYING
			):
				self.drone_ctrl.engine_sound.play()
		
		dt = min(ClockObject.getGlobalClock().getDt(), 0.1)
		self.battery -= dt
		self.run_time += dt
		if self.battery < 0:
			self.battery = 0
			if self.ui_manager.state == 'GAME':
				self.last_attempt_data = "Drone crashed: Battery depleted"
				self.last_attempt_status = False
				self.ui_manager.show_game_over()
		
		self.drone_ctrl.update(dt)
		
		if not self.vr_enabled:
			curr_pos = self.cam_anchor.getPos()
			target_pos = self.cam_target.getPos(self.render)
			self.cam_anchor.setPos(curr_pos + (target_pos - curr_pos) * (10.0 * dt))
			self.cam_anchor.lookAt(self.drone_root.getPos() + Vec3(0, 0, 1.0))
		
		self.level_manager.update(dt, self.drone_root.getPos())
		self.vfx.update(dt)
		speed = self.drone_ctrl.velocity.length()
		self.total_distance += speed * dt
		if speed > self.max_speed_run:
			self.max_speed_run = speed
		self.ui_manager.update_hud(self.level_manager.score, speed, self.battery, self.run_time)
		if self.level_manager.score < 0:
			self.ui_manager.show_game_over()
		if self.level_manager.check_finish(self.drone_root.getPos()):
			avg_speed = self.total_distance / self.run_time if self.run_time > 0 else 0
			self.ui_manager.show_victory(self.level_manager.score, self.run_time, self.max_speed_run, avg_speed)
			self.last_attempt_data = {
				"timestamp": get_iso_datetime(),
				"total_score": self.level_manager.score,
				"time": self.run_time,
				"max_speed": self.max_speed_run,
				"avg_speed": avg_speed
			}
			self.last_attempt_status = True
		return task.cont

	def send_session_analytics(self):
		event = {
			"name": "session_summary",
			"timestamp": get_iso_datetime(),
			"data": {
				"game_started": self.game_started_time,
				"game_closed": get_iso_datetime(),
				"status": self.last_attempt_status,
				"data": self.last_attempt_data
			}
		}
		self.analytics.send(event)

if __name__ == '__main__':
	app = VRDroneSimulatorApp()
	app.run()
