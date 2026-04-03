import sys
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, NodePath, Vec3

from src.config import PATHS, Settings, JSONConfig, Localization, SlotJSONConfig
from src.data import Analytics, DataSave
from src.models import AnalyticsEvent
from src.utils import get_iso_datetime
from src.vr_simulator import VRSimulator
from src.drone_controller import DroneController
from src.ui import UIMenu

class VRDroneSimulatorApp(ShowBase):
    def __init__(self):
        super().__init__()
        
        self.settings = JSONConfig(PATHS['conf']['settings'])
        self.local = Localization(
            PATHS['conf']['local'],
            {'ru': {}, 'en': {}},
            self.settings,
        )
        self.drone_config_manager = SlotJSONConfig(
            PATHS['conf']['drone'],
            {
                'max_speed': 15.0,
                'acceleration': 5.0,
                'rotation_speed': 90.0,
                'battery_life': 300.0,
                'obstacle_penalty': 50
            },
            self.settings,
        )
        self.drone_config = self.drone_config_manager.load()
        self.data_save = DataSave(PATHS['data']['save'], self.settings)
        
        self.setup_scene()
        self.setup_drone()
        
        self.vr_sim = VRSimulator(self)
        self.vr_sim.head_hpr = Vec3(0, -10, 0)
        
        self.drone_ctrl = DroneController(self.drone_root, self.drone_tilt, self.propellers, self.drone_config, self.vr_sim)
        self.ui_menu = UIMenu(self)
        
        self.vr_enabled = False
        try:
            from panda3d_openxr import OpenXRBase
            self.xr = OpenXRBase()
            self.xr.create()
            self.vr_enabled = True
        except:
            pass

        self.camera.reparentTo(self.cam_anchor)
        self.taskMgr.add(self.update_loop, "update_loop")

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
        
        try:
            self.environ = self.loader.loadModel("environment")
            self.environ.reparentTo(self.render)
            self.environ.setScale(0.25, 0.25, 0.25)
            self.environ.setPos(-8, 42, 0)
        except:
            pass

    def setup_drone(self):
        self.drone_root = NodePath("drone_root")
        self.drone_root.reparentTo(self.render)
        self.drone_root.setPos(0, 0, 5)
        
        self.drone_tilt = NodePath("drone_tilt")
        self.drone_tilt.reparentTo(self.drone_root)
        
        try:
            self.drone_model = self.loader.loadModel("src/assets/models/fpv_drone.glb")
            self.drone_model.setScale(0.01)
            self.drone_model.setHpr(90, 0, 0)
            self.propellers = self.drone_model.findAllMatches("**/prop_*")
        except:
            self.drone_model = self.loader.loadModel("box")
            self.drone_model.setScale(0.5)
            self.propellers = [] 
        
        self.drone_model.reparentTo(self.drone_tilt)
        
        self.cam_anchor = NodePath("cam_anchor")
        self.cam_anchor.reparentTo(self.drone_root)
        self.cam_anchor.setPos(0, -6, 2.5)

    def update_loop(self, task):
        if hasattr(self, 'ui_menu') and self.ui_menu.is_open:
            return task.cont
        dt = globalClock.getDt()
        self.drone_ctrl.update(dt)
        if not self.vr_enabled:
            self.camera.setHpr(self.vr_sim.head_hpr)
        return task.cont

if __name__ == "__main__":
    app = VRDroneSimulatorApp()
    app.run()
