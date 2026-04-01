from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3, WindowProperties

class VRSimulator(DirectObject):
    def __init__(self, base):
        self.base = base
        self.left_stick = Vec3(0, 0, 0)
        self.right_stick = Vec3(0, 0, 0)
        self.trigger_pressed = False
        self.grip_pressed = False
        self.head_hpr = Vec3(0, 0, 0)
        
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.base.win.requestProperties(props)
        
        self.accept("w", self.set_stick, ["left", "y", 1])
        self.accept("w-up", self.set_stick, ["left", "y", 0])
        self.accept("s", self.set_stick, ["left", "y", -1])
        self.accept("s-up", self.set_stick, ["left", "y", 0])
        self.accept("a", self.set_stick, ["left", "x", -1])
        self.accept("a-up", self.set_stick, ["left", "x", 0])
        self.accept("d", self.set_stick, ["left", "x", 1])
        self.accept("d-up", self.set_stick, ["left", "x", 0])
        
        self.accept("arrow_up", self.set_stick, ["right", "y", 1])
        self.accept("arrow_up-up", self.set_stick, ["right", "y", 0])
        self.accept("arrow_down", self.set_stick, ["right", "y", -1])
        self.accept("arrow_down-up", self.set_stick, ["right", "y", 0])
        self.accept("arrow_left", self.set_stick, ["right", "x", -1])
        self.accept("arrow_left-up", self.set_stick, ["right", "x", 0])
        self.accept("arrow_right", self.set_stick, ["right", "x", 1])
        self.accept("arrow_right-up", self.set_stick, ["right", "x", 0])
        
        self.accept("space", self.set_trigger, [True])
        self.accept("space-up", self.set_trigger, [False])
        self.accept("shift", self.set_grip, [True])
        self.accept("shift-up", self.set_grip, [False])
        
        self.accept("escape", __import__('sys').exit, [0])

        self.base.taskMgr.add(self.update_mouse, "vr_mouse_task")

    def set_stick(self, stick, axis, val):
        if stick == "left":
            if axis == "y": self.left_stick.y = val
            if axis == "x": self.left_stick.x = val
        elif stick == "right":
            if axis == "y": self.right_stick.y = val
            if axis == "x": self.right_stick.x = val

    def set_trigger(self, state):
        self.trigger_pressed = state

    def set_grip(self, state):
        self.grip_pressed = state

    def update_mouse(self, task):
        if self.base.mouseWatcherNode.hasMouse():
            x = self.base.mouseWatcherNode.getMouseX()
            y = self.base.mouseWatcherNode.getMouseY()
            self.head_hpr.x -= x * 100
            self.head_hpr.y += y * 100
            self.head_hpr.y = max(-80, min(80, self.head_hpr.y))
            self.base.win.movePointer(0, self.base.win.getXSize() // 2, self.base.win.getYSize() // 2)
        return task.cont
