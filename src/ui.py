import sys
import os
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from panda3d.core import WindowProperties, TextNode, MouseButton

UI_TEXT = {
    'en': {
        'main_title': 'DRONE SIMULATOR', 'play': 'PLAY', 'settings': 'SETTINGS', 'exit': 'EXIT',
        'pause_title': 'PAUSED', 'resume': 'RESUME', 'main_menu': 'MAIN MENU',
        'settings_title': 'Settings', 'language': 'Language', 'save_slot': 'Save Slot',
        'back': 'BACK', 'reset': 'RESET DEFAULTS', 'max_speed': 'Max Speed',
        'acceleration': 'Acceleration', 'rotation_speed': 'Rotation Speed',
        'battery_life': 'Battery Life', 'obstacle_penalty': 'Obstacle Penalty'
    },
    'ru': {
        'main_title': 'СИМУЛЯТОР ДРОНА', 'play': 'ИГРАТЬ', 'settings': 'НАСТРОЙКИ', 'exit': 'ВЫХОД',
        'pause_title': 'ПАУЗА', 'resume': 'ПРОДОЛЖИТЬ', 'main_menu': 'ГЛАВНОЕ МЕНЮ',
        'settings_title': 'Настройки', 'language': 'Язык', 'save_slot': 'Слот сохранения',
        'back': 'НАЗАД', 'reset': 'ПО УМОЛЧАНИЮ', 'max_speed': 'Макс. скорость',
        'acceleration': 'Ускорение', 'rotation_speed': 'Скор. вращения',
        'battery_life': 'Заряд батареи', 'obstacle_penalty': 'Штраф препятствий'
    }
}

RANGES = {
    'max_speed': (2.0, 25.0), 'acceleration': (1.0, 15.0),
    'rotation_speed': (10.0, 150.0), 'battery_life': (60.0, 1200.0), 'obstacle_penalty': (0, 100)
}

DEFAULTS = {
    'max_speed': 15.0, 'acceleration': 5.0, 'rotation_speed': 90.0,
    'battery_life': 300.0, 'obstacle_penalty': 50.0
}

def get_cyrillic_font(loader):
    paths = [
        'C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/System/Library/Fonts/Helvetica.ttc'
    ]
    for p in paths:
        if os.path.exists(p):
            f = loader.loadFont(p)
            if f.isValid():
                f.setPixelsPerUnit(60)
                return f
    return TextNode.getDefaultFont()

class SegmentedControl:
    def __init__(self, parent, items, pos, initial_idx, command, font):
        self.command = command
        self.buttons = []
        self.current_idx = initial_idx
        for i, item in enumerate(items):
            btn = DirectButton(parent=parent, text=item, pos=(pos[0] + i * 0.15, 0, pos[2]),
                               scale=0.045, frameSize=(-1.5, 1.5, -0.4, 0.7), relief=DGG.FLAT,
                               text_font=font, command=self.select, extraArgs=[i, item])
            self.buttons.append(btn)
        self.update_colors()
        
    def select(self, idx, item):
        self.current_idx = idx
        self.update_colors()
        self.command(item)
        
    def update_colors(self):
        for i, btn in enumerate(self.buttons):
            if i == self.current_idx:
                btn['frameColor'] = (0.2, 0.6, 0.8, 1)
                btn['text_fg'] = (1, 1, 1, 1)
            else:
                btn['frameColor'] = (0.15, 0.15, 0.18, 1)
                btn['text_fg'] = (0.5, 0.5, 0.5, 1)

class CustomSlider:
    def __init__(self, app, parent, pos, range_vals, initial_val, command, font):
        self.app = app
        self.command = command
        self.min_val, self.max_val = range_vals
        self.width = 0.5
        self.val = initial_val
        self.is_dragging = False
        
        self.track = DirectFrame(parent=parent, pos=pos, frameSize=(0, self.width, -0.005, 0.005), frameColor=(0.15, 0.15, 0.15, 1))
        self.fill = DirectFrame(parent=parent, pos=pos, frameSize=(0, 0, -0.005, 0.005), frameColor=(0.2, 0.6, 0.8, 1))
        self.thumb = DirectButton(parent=parent, pos=(pos[0], 0, pos[2]), frameSize=(-0.015, 0.015, -0.03, 0.03), relief=DGG.FLAT, frameColor=(0.9, 0.9, 0.9, 1))
        self.val_label = DirectLabel(parent=parent, text=f"{self.val:.1f}", pos=(pos[0] + self.width + 0.05, 0, pos[2] - 0.015), scale=0.045, text_fg=(1, 1, 1, 1), text_font=font, frameColor=(0,0,0,0), text_align=TextNode.ALeft)
        
        self.thumb.bind(DGG.B1PRESS, self.start_drag)
        self.thumb.bind(DGG.B1RELEASE, self.stop_drag)
        self.app.taskMgr.add(self.drag_task, f"drag_task_{id(self)}")
        self.update_ui()
        
    def set_val(self, val):
        self.val = max(self.min_val, min(self.max_val, val))
        self.update_ui()
        
    def update_ui(self):
        percent = (self.val - self.min_val) / (self.max_val - self.min_val)
        cx = self.track.getPos()[0] + percent * self.width
        self.thumb.setPos(cx, 0, self.track.getPos()[2])
        self.fill['frameSize'] = (0, percent * self.width, -0.005, 0.005)
        self.val_label['text'] = f"{self.val:.1f}"
        
    def start_drag(self, event): 
        self.is_dragging = True
        
    def stop_drag(self, event): 
        self.is_dragging = False
    
    def drag_task(self, task):
        if self.is_dragging and self.app.mouseWatcherNode.hasMouse():
            m_x = self.app.mouseWatcherNode.getMouse().getX() * self.app.getAspectRatio()
            local_x = m_x - self.track.getPos(self.app.aspect2d).getX()
            percent = max(0.0, min(1.0, local_x / self.width))
            self.val = self.min_val + percent * (self.max_val - self.min_val)
            self.update_ui()
            self.command(self.val)
        if not self.app.mouseWatcherNode.isButtonDown(MouseButton.one()):
            self.is_dragging = False
        return task.cont

class HoverButton:
    def __init__(self, parent, text, pos, command, font, color1, scale=0.055, frameSize=(-4.5, 4.5, -0.6, 0.9)):
        self.btn = DirectButton(parent=parent, text=text, pos=pos, scale=scale,
                                frameSize=frameSize, relief=DGG.FLAT,
                                frameColor=color1, text_fg=(1, 1, 1, 1),
                                text_font=font, command=command)
        self.btn.bind(DGG.WITHIN, lambda e: self.btn.setColorScale(1.3, 1.3, 1.3, 1))
        self.btn.bind(DGG.WITHOUT, lambda e: self.btn.setColorScale(1, 1, 1, 1))
        
    def set_text(self, text):
        self.btn['text'] = text

class UIManager:
    def __init__(self, app):
        self.app = app
        self.font = get_cyrillic_font(self.app.loader)
        self.current_lang = self.app.settings.load().get('language', 'en')
        if self.current_lang not in UI_TEXT: 
            self.current_lang = 'en'
            
        self.main_frame = DirectFrame(frameSize=(-2, 2, -1, 1), frameColor=(0.08, 0.09, 0.11, 1), pos=(0, 0, 0))
        self.pause_frame = DirectFrame(frameSize=(-2, 2, -1, 1), frameColor=(0.08, 0.09, 0.11, 0.85), pos=(0, 0, 0))
        self.settings_frame = DirectFrame(frameSize=(-0.9, 0.9, -0.85, 0.85), frameColor=(0.08, 0.09, 0.11, 0.98), pos=(0, 0, 0))
        
        self.build_main_menu()
        self.build_pause_menu()
        self.build_settings_menu()
        
        self.state = 'MAIN'
        self.prev_state = 'MAIN'
        self.app.accept('escape', self.handle_escape)
        self.update_all_texts()
        self.show_main()
        
    def build_main_menu(self):
        self.main_title = DirectLabel(parent=self.main_frame, text="", scale=0.12, pos=(0, 0, 0.5), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0,0,0,0))
        self.main_play_btn = HoverButton(self.main_frame, "", (0, 0, 0.1), self.start_game, self.font, (0.15, 0.3, 0.2, 1), scale=0.065)
        self.main_set_btn = HoverButton(self.main_frame, "", (0, 0, -0.15), lambda: self.show_settings('MAIN'), self.font, (0.2, 0.2, 0.25, 1), scale=0.065)
        self.main_exit_btn = HoverButton(self.main_frame, "", (0, 0, -0.4), sys.exit, self.font, (0.3, 0.15, 0.15, 1), scale=0.065)

    def build_pause_menu(self):
        self.pause_title = DirectLabel(parent=self.pause_frame, text="", scale=0.12, pos=(0, 0, 0.5), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0,0,0,0))
        self.pause_res_btn = HoverButton(self.pause_frame, "", (0, 0, 0.15), self.resume_game, self.font, (0.15, 0.3, 0.2, 1), scale=0.06)
        self.pause_set_btn = HoverButton(self.pause_frame, "", (0, 0, -0.05), lambda: self.show_settings('PAUSE'), self.font, (0.2, 0.2, 0.25, 1), scale=0.06)
        self.pause_main_btn = HoverButton(self.pause_frame, "", (0, 0, -0.25), self.show_main, self.font, (0.2, 0.2, 0.2, 1), scale=0.06)
        self.pause_exit_btn = HoverButton(self.pause_frame, "", (0, 0, -0.45), sys.exit, self.font, (0.3, 0.15, 0.15, 1), scale=0.06)

    def build_settings_menu(self):
        self.settings_title = DirectLabel(parent=self.settings_frame, text="", scale=0.08, pos=(0, 0, 0.7), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0,0,0,0))
        
        self.labels = {}
        self.labels['language'] = DirectLabel(parent=self.settings_frame, text="", scale=0.045, pos=(-0.7, 0, 0.5), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0,0,0,0))
        lang_idx = 0 if self.current_lang == 'en' else 1
        self.lang_ctrl = SegmentedControl(self.settings_frame, ['en', 'ru'], (-0.2, 0, 0.5), lang_idx, self.change_lang, self.font)
        
        self.labels['save_slot'] = DirectLabel(parent=self.settings_frame, text="", scale=0.045, pos=(-0.7, 0, 0.4), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0,0,0,0))
        slot = str(self.app.settings.load().get('save_slot', '1'))
        slot_idx = int(slot) - 1 if slot.isdigit() and 1 <= int(slot) <= 3 else 0
        self.slot_ctrl = SegmentedControl(self.settings_frame, ['1', '2', '3'], (-0.2, 0, 0.4), slot_idx, self.change_slot, self.font)
        
        self.sliders = {}
        y_pos = 0.2
        for key in ['max_speed', 'acceleration', 'rotation_speed', 'battery_life', 'obstacle_penalty']:
            val = self.app.drone_config.get(key, DEFAULTS[key])
            lbl = DirectLabel(parent=self.settings_frame, text="", scale=0.045, pos=(-0.7, 0, y_pos), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0,0,0,0))
            self.labels[key] = lbl
            
            slider = CustomSlider(self.app, self.settings_frame, (-0.2, 0, y_pos+0.015), RANGES[key], val, lambda v, k=key: self.update_param(k, v), self.font)
            self.sliders[key] = slider
            y_pos -= 0.12
            
        self.set_reset_btn = HoverButton(self.settings_frame, "", (-0.3, 0, -0.6), self.reset_defaults, self.font, (0.3, 0.15, 0.15, 1))
        self.set_back_btn = HoverButton(self.settings_frame, "", (0.3, 0, -0.6), self.close_settings, self.font, (0.15, 0.3, 0.2, 1))

    def get_text(self, key): 
        return UI_TEXT[self.current_lang].get(key, key)
    
    def update_all_texts(self):
        self.main_title['text'] = self.get_text('main_title')
        self.main_play_btn.set_text(self.get_text('play'))
        self.main_set_btn.set_text(self.get_text('settings'))
        self.main_exit_btn.set_text(self.get_text('exit'))
        
        self.pause_title['text'] = self.get_text('pause_title')
        self.pause_res_btn.set_text(self.get_text('resume'))
        self.pause_set_btn.set_text(self.get_text('settings'))
        self.pause_main_btn.set_text(self.get_text('main_menu'))
        self.pause_exit_btn.set_text(self.get_text('exit'))
        
        self.settings_title['text'] = self.get_text('settings_title')
        self.labels['language']['text'] = self.get_text('language')
        self.labels['save_slot']['text'] = self.get_text('save_slot')
        self.set_reset_btn.set_text(self.get_text('reset'))
        self.set_back_btn.set_text(self.get_text('back'))
        for key in self.sliders.keys():
            self.labels[key]['text'] = self.get_text(key)
            
    def change_lang(self, lang):
        self.current_lang = lang
        d = self.app.settings.load()
        d['language'] = lang
        self.app.settings.dump(d)
        self.update_all_texts()
        
    def change_slot(self, slot):
        d = self.app.settings.load()
        d['save_slot'] = str(slot)
        self.app.settings.dump(d)
        if hasattr(self.app, 'data_save'): 
            self.app.data_save.slot = str(slot)
        
    def update_param(self, key, val):
        self.app.drone_config[key] = val
        
    def reset_defaults(self):
        for k, v in DEFAULTS.items():
            self.sliders[k].set_val(v)
            self.app.drone_config[k] = v
            
    def hide_all(self):
        self.main_frame.hide()
        self.pause_frame.hide()
        self.settings_frame.hide()
        
    def show_main(self):
        self.state = 'MAIN'
        self.hide_all()
        self.main_frame.show()
        self.apply_mouse_state(True)
        if hasattr(self.app, 'drone_root'):
            self.app.drone_root.setPos(0, 0, 5)
            self.app.drone_ctrl.velocity.set(0, 0, 0)
            self.app.drone_ctrl.current_pitch = 0
            self.app.drone_ctrl.current_roll = 0
            self.app.drone_ctrl.current_throttle = 0
        
    def start_game(self):
        self.state = 'GAME'
        self.hide_all()
        self.apply_mouse_state(False)
        
    def show_pause(self):
        self.state = 'PAUSE'
        self.hide_all()
        self.pause_frame.show()
        self.apply_mouse_state(True)
        
    def resume_game(self):
        self.start_game()
        
    def show_settings(self, prev_state):
        self.prev_state = prev_state
        self.state = 'SETTINGS'
        self.hide_all()
        self.settings_frame.show()
        self.apply_mouse_state(True)
        
    def close_settings(self):
        self.app.drone_config_manager.dump(self.app.drone_config)
        if self.prev_state == 'MAIN':
            self.show_main()
        else:
            self.show_pause()
            
    def handle_escape(self):
        if self.state == 'GAME':
            self.show_pause()
        elif self.state == 'PAUSE':
            self.resume_game()
        elif self.state == 'SETTINGS':
            self.close_settings()
            
    def apply_mouse_state(self, show_cursor):
        props = WindowProperties()
        if show_cursor:
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
        else:
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_relative)
            if self.app.win: 
                self.app.win.movePointer(0, self.app.win.getXSize() // 2, self.app.win.getYSize() // 2)
        self.app.win.requestProperties(props)
