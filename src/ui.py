import sys
import os
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from panda3d.core import WindowProperties, TextNode, MouseButton, Vec3
from src.config import PATHS, RANGES, DEFAULTS, UI_TEXT

def get_cyrillic_font(loader):
	paths = PATHS.get('assets', {}).get('fonts', [])
	for p in paths:
		if os.path.exists(p):
			f = loader.loadFont(p)
			if f.isValid():
				f.setPixelsPerUnit(60)
				return f
	return TextNode.getDefaultFont()

class UIComponent:
	def show(self):
		if hasattr(self, 'node'):
			self.node.show()
	def hide(self):
		if hasattr(self, 'node'):
			self.node.hide()
	def destroy(self):
		if hasattr(self, 'node'):
			self.node.destroy()

class AutoButton(UIComponent):
	def __init__(self, parent, text, pos, command, font, color, scale=0.06):
		self.btn = DirectButton(
			parent=parent,
			text=text,
			pos=pos,
			scale=scale,
			pad=(1.0, 0.4),
			relief=DGG.FLAT,
			frameColor=color,
			text_fg=(1, 1, 1, 1),
			text_font=font,
			command=command,
			text_align=TextNode.ACenter,
			text_pos=(0, -0.2)
		)
		self.btn.bind(DGG.WITHIN, lambda e: self.btn.setColorScale(1.2, 1.2, 1.2, 1))
		self.btn.bind(DGG.WITHOUT, lambda e: self.btn.setColorScale(1, 1, 1, 1))
		self.node = self.btn

	def set_text(self, text):
		self.btn['text'] = text
		self.btn.resetFrameSize()

class SegmentedControl(UIComponent):
	def __init__(self, parent, items, pos, initial_idx, command, font):
		self.command = command
		self.buttons = []
		self.current_idx = initial_idx
		self.node = DirectFrame(parent=parent, pos=pos, frameColor=(0,0,0,0))
		for i, item in enumerate(items):
			btn = DirectButton(
				parent=self.node,
				text=item,
				pos=(i * 0.35, 0, 0),
				scale=0.045,
				pad=(0.8, 0.3),
				relief=DGG.FLAT,
				text_font=font,
				command=self.select,
				extraArgs=[i, item],
				text_align=TextNode.ACenter,
				text_pos=(0, -0.2)
			)
			btn.resetFrameSize()
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

class CustomSlider(UIComponent):
	def __init__(self, app, parent, pos, range_vals, initial_val, command, font):
		self.app = app
		self.command = command
		self.min_val, self.max_val = range_vals
		self.width = 0.5
		self.val = initial_val
		self.is_dragging = False
		self.node = DirectFrame(parent=parent, pos=pos, frameColor=(0,0,0,0))
		self.track = DirectFrame(
			parent=self.node, pos=(0, 0, 0), frameSize=(0, self.width, -0.005, 0.005), frameColor=(0.15, 0.15, 0.15, 1)
		)
		self.fill = DirectFrame(parent=self.node, pos=(0, 0, 0), frameSize=(0, 0, -0.005, 0.005), frameColor=(0.2, 0.6, 0.8, 1))
		self.thumb = DirectButton(
			parent=self.node,
			pos=(0, 0, 0),
			frameSize=(-0.015, 0.015, -0.03, 0.03),
			relief=DGG.FLAT,
			frameColor=(0.9, 0.9, 0.9, 1),
		)
		self.val_label = DirectLabel(
			parent=self.node,
			text=f'{self.val:.1f}',
			pos=(self.width + 0.05, 0, -0.015),
			scale=0.045,
			text_fg=(1, 1, 1, 1),
			text_font=font,
			frameColor=(0, 0, 0, 0),
			text_align=TextNode.ALeft,
		)
		self.thumb.bind(DGG.B1PRESS, self.start_drag)
		self.thumb.bind(DGG.B1RELEASE, self.stop_drag)
		self.app.taskMgr.add(self.drag_task, f'drag_task_{id(self)}')
		self.update_ui()

	def set_val(self, val):
		self.val = max(self.min_val, min(self.max_val, val))
		self.update_ui()

	def update_ui(self):
		percent = (self.val - self.min_val) / (self.max_val - self.min_val)
		cx = percent * self.width
		self.thumb.setPos(cx, 0, 0)
		self.fill['frameSize'] = (0, percent * self.width, -0.005, 0.005)
		self.val_label['text'] = f'{self.val:.1f}'

	def start_drag(self, event):
		self.is_dragging = True

	def stop_drag(self, event):
		self.is_dragging = False

	def drag_task(self, task):
		if self.is_dragging and self.app.mouseWatcherNode.hasMouse():
			m_x = self.app.mouseWatcherNode.getMouse().getX() * self.app.getAspectRatio()
			local_x = m_x - self.node.getPos(self.app.aspect2d).getX()
			percent = max(0.0, min(1.0, local_x / self.width))
			self.val = self.min_val + percent * (self.max_val - self.min_val)
			self.update_ui()
			self.command(self.val)
		if not self.app.mouseWatcherNode.isButtonDown(MouseButton.one()):
			self.is_dragging = False
		return task.cont

class MenuLayout(UIComponent):
	def __init__(self, parent, font, bg_color):
		self.node = DirectFrame(parent=parent, frameSize=(-10, 10, -10, 10), frameColor=bg_color)
		self.font = font
		self.buttons = []
		self.title = DirectLabel(
			parent=self.node,
			text='',
			scale=0.12,
			pos=(0, 0, 0.5),
			text_fg=(1, 1, 1, 1),
			text_font=self.font,
			frameColor=(0, 0, 0, 0)
		)

	def add_button(self, text, command, color, y_offset):
		btn = AutoButton(self.node, text, (0, 0, y_offset), command, self.font, color)
		self.buttons.append(btn)
		return btn

	def set_title(self, text):
		self.title['text'] = text

class UIManager:
	def __init__(self, app):
		self.app = app
		self.font = get_cyrillic_font(self.app.loader)
		self.current_lang = self.app.settings.load().get('language', 'en')
		if self.current_lang not in ['en', 'ru']:
			self.current_lang = 'en'
		self.aspect2d = self.app.aspect2d
		self.main_menu = MenuLayout(self.aspect2d, self.font, (0.08, 0.09, 0.11, 1))
		self.pause_menu = MenuLayout(self.aspect2d, self.font, (0.08, 0.09, 0.11, 0.85))
		self.game_over_menu = MenuLayout(self.aspect2d, self.font, (0.15, 0.05, 0.05, 0.9))
		self.settings_frame = DirectFrame(parent=self.aspect2d, frameSize=(-10, 10, -10, 10), frameColor=(0.08, 0.09, 0.11, 0.98))
		self.hud_frame = DirectFrame(parent=self.app.a2dTopLeft, frameSize=(0, 0, 0, 0), frameColor=(0, 0, 0, 0))
		self.victory_frame = DirectFrame(parent=self.aspect2d, frameSize=(-10, 10, -10, 10), frameColor=(0.08, 0.09, 0.11, 0.95))
		
		self.build_main_menu()
		self.build_pause_menu()
		self.build_game_over_menu()
		self.build_settings_menu()
		self.build_hud()
		self.build_victory_menu()
		
		self.state = 'MAIN'
		self.prev_state = 'MAIN'
		self.app.accept('escape', self.handle_escape)
		self.update_all_texts()
		self.show_main()

	def build_main_menu(self):
		self.btn_play = self.main_menu.add_button('', self.start_game, (0.15, 0.3, 0.2, 1), 0.1)
		self.btn_settings = self.main_menu.add_button('', lambda: self.show_settings('MAIN'), (0.2, 0.2, 0.25, 1), -0.15)
		self.btn_exit = self.main_menu.add_button('', sys.exit, (0.3, 0.15, 0.15, 1), -0.4)

	def build_pause_menu(self):
		self.btn_resume = self.pause_menu.add_button('', self.resume_game, (0.15, 0.3, 0.2, 1), 0.15)
		self.btn_p_settings = self.pause_menu.add_button('', lambda: self.show_settings('PAUSE'), (0.2, 0.2, 0.25, 1), -0.1)
		self.btn_p_main = self.pause_menu.add_button('', self.show_main, (0.2, 0.2, 0.2, 1), -0.35)

	def build_game_over_menu(self):
		self.btn_go_restart = self.game_over_menu.add_button('', self.restart_game, (0.15, 0.3, 0.2, 1), 0.1)
		self.btn_go_main = self.game_over_menu.add_button('', self.show_main, (0.2, 0.2, 0.2, 1), -0.15)

	def build_settings_menu(self):
		self.settings_title = DirectLabel(parent=self.settings_frame, text='', scale=0.08, pos=(0, 0, 0.7), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0))
		self.labels = {}
		self.labels['language'] = DirectLabel(parent=self.settings_frame, text='', scale=0.045, pos=(-0.5, 0, 0.5), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0, 0, 0, 0))
		lang_idx = 0 if self.current_lang == 'en' else 1
		self.lang_ctrl = SegmentedControl(self.settings_frame, ['en', 'ru'], (-0.1, 0, 0.5), lang_idx, self.change_lang, self.font)
		self.labels['save_slot'] = DirectLabel(parent=self.settings_frame, text='', scale=0.045, pos=(-0.5, 0, 0.4), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0, 0, 0, 0))
		slot = str(self.app.settings.load().get('save_slot', '1'))
		slot_idx = int(slot) - 1 if slot.isdigit() and 1 <= int(slot) <= 3 else 0
		self.slot_ctrl = SegmentedControl(self.settings_frame, ['1', '2', '3'], (-0.1, 0, 0.4), slot_idx, self.change_slot, self.font)
		self.sliders = {}
		y_pos = 0.2
		keys = ['max_speed', 'acceleration', 'rotation_speed', 'battery_life', 'obstacle_penalty']
		for key in keys:
			val = self.app.drone_config.get(key, DEFAULTS[key])
			lbl = DirectLabel(parent=self.settings_frame, text='', scale=0.045, pos=(-0.5, 0, y_pos), text_fg=(0.7, 0.7, 0.7, 1), text_align=TextNode.ALeft, text_font=self.font, frameColor=(0, 0, 0, 0))
			self.labels[key] = lbl
			slider = CustomSlider(self.app, self.settings_frame, (-0.1, 0, y_pos), RANGES[key], val, lambda v, k=key: self.update_param(k, v), self.font)
			self.sliders[key] = slider
			y_pos -= 0.12
		self.btn_s_reset = AutoButton(self.settings_frame, '', (-0.4, 0, -0.6), self.reset_defaults, self.font, (0.3, 0.15, 0.15, 1))
		self.btn_s_back = AutoButton(self.settings_frame, '', (0.4, 0, -0.6), self.close_settings, self.font, (0.15, 0.3, 0.2, 1))

	def build_hud(self):
		self.hud_score = DirectLabel(parent=self.app.a2dTopLeft, text='', scale=0.07, pos=(0.1, 0, -0.1), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0), text_align=TextNode.ALeft)
		self.hud_battery = DirectLabel(parent=self.app.a2dTopRight, text='', scale=0.07, pos=(-0.1, 0, -0.1), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0), text_align=TextNode.ARight)
		self.hud_speed = DirectLabel(parent=self.app.a2dBottomLeft, text='', scale=0.07, pos=(0.1, 0, 0.2), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0), text_align=TextNode.ALeft)
		self.hud_time = DirectLabel(parent=self.app.a2dBottomRight, text='', scale=0.07, pos=(-0.1, 0, 0.2), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0), text_align=TextNode.ARight)

	def build_victory_menu(self):
		self.vic_title = DirectLabel(parent=self.victory_frame, text='', scale=0.12, pos=(0, 0, 0.75), text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0, 0, 0, 0))
		self.cards_container = DirectFrame(parent=self.victory_frame, frameColor=(0,0,0,0))
		self.btn_v_restart = AutoButton(self.victory_frame, '', (-0.3, 0, -0.75), self.restart_game, self.font, (0.15, 0.3, 0.2, 1))
		self.btn_v_main = AutoButton(self.victory_frame, '', (0.3, 0, -0.75), self.show_main, self.font, (0.2, 0.2, 0.2, 1))

	def create_card(self, parent, pos, title, score, time, avg_spd, max_spd, config_str, highlight=False, active_slot=False):
		w = 0.4 if highlight else 0.32
		h = 0.22
		bg_color = (0.25, 0.2, 0.1, 1) if highlight else (0.15, 0.18, 0.22, 1)
		border_color = (0.8, 0.6, 0.1, 1) if highlight else ((0.3, 0.6, 0.8, 1) if active_slot else (0.2, 0.3, 0.4, 1))
		border = DirectFrame(parent=parent, pos=pos, frameSize=(-w-0.01, w+0.01, -h-0.01, h+0.01), frameColor=border_color)
		card = DirectFrame(parent=border, pos=(0,0,0), frameSize=(-w, w, -h, h), frameColor=bg_color)
		lang = self.current_lang
		pts_str = 'очков' if lang == 'ru' else 'pts'
		title_color = (1, 0.9, 0.2, 1) if highlight else ((0.5, 0.8, 1, 1) if active_slot else (0.8, 0.8, 0.8, 1))
		DirectLabel(parent=card, text=title, pos=(0, 0, h - 0.06), scale=0.05 if highlight else 0.045, text_fg=title_color, text_font=self.font, frameColor=(0,0,0,0))
		if config_str == "---":
			DirectLabel(parent=card, text="--- ПУСТО ---" if lang == 'ru' else "--- EMPTY ---", pos=(0, 0, -0.05), scale=0.04, text_fg=(0.5, 0.5, 0.5, 1), text_font=self.font, frameColor=(0,0,0,0))
			return
		DirectLabel(parent=card, text=f"{float(score):.1f} {pts_str}", pos=(0, 0, h - 0.16), scale=0.07 if highlight else 0.06, text_fg=(1, 1, 1, 1), text_font=self.font, frameColor=(0,0,0,0))
		time_lbl = 'Время' if lang == 'ru' else 'Time'
		avg_lbl = 'Ср.Скор' if lang == 'ru' else 'AvgSpd'
		max_lbl = 'Макс.Скор' if lang == 'ru' else 'MaxSpd'
		stats = f"{time_lbl}: {time:.1f}s   |   {avg_lbl}: {avg_spd:.1f}\n{max_lbl}: {max_spd:.1f}"
		DirectLabel(parent=card, text=stats, pos=(0, 0, -0.02 if highlight else 0.0), scale=0.035, text_fg=(0.8, 0.8, 0.8, 1), text_font=self.font, frameColor=(0,0,0,0))
		if config_str:
			DirectLabel(parent=card, text=config_str, pos=(0, 0, -h + 0.07), scale=0.03, text_fg=(0.5, 0.6, 0.7, 1), text_font=self.font, frameColor=(0,0,0,0), text_align=TextNode.ACenter)

	def get_text(self, key):
		return UI_TEXT.get(self.current_lang, {}).get(key, key)

	def update_all_texts(self):
		self.main_menu.set_title(self.get_text('main_title'))
		self.btn_play.set_text(self.get_text('play'))
		self.btn_settings.set_text(self.get_text('settings'))
		self.btn_exit.set_text(self.get_text('exit'))
		self.pause_menu.set_title(self.get_text('pause_title'))
		self.btn_resume.set_text(self.get_text('resume'))
		self.btn_p_settings.set_text(self.get_text('settings'))
		self.btn_p_main.set_text(self.get_text('main_menu'))
		self.game_over_menu.set_title(self.get_text('game_over_title'))
		self.btn_go_restart.set_text(self.get_text('restart'))
		self.btn_go_main.set_text(self.get_text('main_menu'))
		self.settings_title['text'] = self.get_text('settings_title')
		self.btn_s_reset.set_text(self.get_text('reset'))
		self.btn_s_back.set_text(self.get_text('back'))
		self.vic_title['text'] = self.get_text('victory_title')
		self.btn_v_restart.set_text(self.get_text('restart'))
		self.btn_v_main.set_text(self.get_text('main_menu'))
		if hasattr(self, 'labels'):
			self.labels['language']['text'] = self.get_text('language')
			self.labels['save_slot']['text'] = self.get_text('save_slot')
			for key in self.sliders:
				self.labels[key]['text'] = self.get_text(key)

	def update_hud(self, score, speed, battery, time):
		self.hud_score['text'] = f'{self.get_text("score")} {int(score)}'
		self.hud_speed['text'] = f'{self.get_text("speed")} {int(speed)}'
		self.hud_battery['text'] = f'{self.get_text("battery")} {int(battery)}s'
		self.hud_time['text'] = f'{self.get_text("time")} {time:.1f}s'

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
			self.app.data_save._slot = str(slot)
			self.app.data_save._save = self.app.data_save.load()
		if hasattr(self.app, 'local'):
			self.app.local._slot = str(slot)
		if hasattr(self.app, 'drone_config_manager'):
			self.app.drone_config_manager._slot = str(slot)
			self.app.drone_config = self.app.drone_config_manager.load()
		for k in self.sliders:
			self.sliders[k].set_val(self.app.drone_config.get(k, DEFAULTS[k]))
		self.update_all_texts()

	def update_param(self, key, val):
		self.app.drone_config[key] = val

	def reset_defaults(self):
		for k, v in DEFAULTS.items():
			self.app.drone_config[k] = v
			if k in self.sliders:
				self.sliders[k].set_val(v)

	def hide_all(self):
		self.main_menu.hide()
		self.pause_menu.hide()
		self.game_over_menu.hide()
		self.settings_frame.hide()
		self.hud_frame.hide()
		self.hud_score.hide()
		self.hud_speed.hide()
		self.hud_battery.hide()
		self.hud_time.hide()
		self.victory_frame.hide()

	def show_main(self):
		self.state = 'MAIN'
		self.hide_all()
		self.main_menu.show()
		self.apply_mouse_state(True)
		if hasattr(self.app, 'drone_root'):
			self.app.drone_root.setPos(0, 0, 5)
			self.app.drone_ctrl.velocity.set(0, 0, 0)
			self.app.drone_root.setHpr(0, 0, 0)
			if hasattr(self.app, 'cam_anchor') and hasattr(self.app, 'cam_target'):
				self.app.cam_anchor.setPos(self.app.cam_target.getPos(self.app.render))
				self.app.cam_anchor.lookAt(self.app.drone_root.getPos() + Vec3(0, 0, 1.0))
		if hasattr(self.app, 'level_manager'):
			self.app.level_manager.reset()
		if hasattr(self.app, 'battery'):
			self.app.battery = float(self.app.drone_config.get('battery_life', 300.0))
			self.app.run_time = 0.0
			self.app.max_speed_run = 0.0
			self.app.total_distance = 0.0

	def show_game_over(self):
		self.state = 'GAME_OVER'
		self.hide_all()
		self.game_over_menu.show()
		self.apply_mouse_state(True)

	def show_victory(self, score, time, max_speed, avg_speed):
		self.state = 'VICTORY'
		self.hide_all()
		self.victory_frame.show()
		self.apply_mouse_state(True)
		
		all_saves = self.app.data_save.load(all_=True)
		current_save = all_saves.get(self.app.data_save._slot, {})
		best_score = float(current_save.get('total_score', -1))
		best_time = current_save.get('best_time', float('inf'))
		if best_time == 0.0:
			best_time = float('inf')
			
		is_new_best = False
		if score > best_score:
			is_new_best = True
		elif score == best_score and time < best_time:
			is_new_best = True
			
		if is_new_best:
			self.app.data_save.dump(
				best_time=time,
				total_score=score,
				avg_speed=avg_speed,
				max_speed=max_speed,
				drone_config=self.app.drone_config
			)
			all_saves = self.app.data_save.load(all_=True)

		for child in self.cards_container.getChildren():
			child.removeNode()

		lang = self.current_lang
		curr_title = 'Текущий заезд' if lang == 'ru' else 'Current Run'
		cfg = self.app.drone_config
		spd_lbl = 'Скор' if lang == 'ru' else 'Spd'
		acc_lbl = 'Уск' if lang == 'ru' else 'Acc'
		rot_lbl = 'Вращ' if lang == 'ru' else 'Rot'
		bat_lbl = 'Бат' if lang == 'ru' else 'Bat'
		pen_lbl = 'Штраф' if lang == 'ru' else 'Pen'
		curr_cfg_str = f"{spd_lbl}:{cfg.get('max_speed',0):.0f} {acc_lbl}:{cfg.get('acceleration',0):.0f} {rot_lbl}:{cfg.get('rotation_speed',0):.0f}\n{bat_lbl}:{cfg.get('battery_life',0):.0f} {pen_lbl}:{cfg.get('obstacle_penalty',0):.0f}"
		
		self.create_card(self.cards_container, (0, 0, 0.35), curr_title, score, time, avg_speed, max_speed, curr_cfg_str, highlight=True)

		slot_x = -0.72
		for i in range(1, 4):
			slot_id = str(i)
			save_data = all_saves.get(slot_id, {})
			sc = float(save_data.get('total_score', 0))
			t = float(save_data.get('best_time', 0.0))
			av = float(save_data.get('avg_speed', 0.0))
			mx = float(save_data.get('max_speed', 0.0))
			slot_cfg = save_data.get('drone_config', {})
			
			if sc > 0 or t > 0:
				cfg_str = f"{spd_lbl}:{slot_cfg.get('max_speed',0):.0f} {acc_lbl}:{slot_cfg.get('acceleration',0):.0f} {rot_lbl}:{slot_cfg.get('rotation_speed',0):.0f}\n{bat_lbl}:{slot_cfg.get('battery_life',0):.0f} {pen_lbl}:{slot_cfg.get('obstacle_penalty',0):.0f}"
			else:
				cfg_str = "---"
				sc, t, av, mx = 0.0, 0.0, 0.0, 0.0
				
			is_active = (slot_id == self.app.data_save._slot)
			self.create_card(self.cards_container, (slot_x, 0, -0.25), f"{self.get_text('slot_name')} {slot_id}", sc, t, av, mx, cfg_str, highlight=False, active_slot=is_active)
			slot_x += 0.72

	def restart_game(self):
		self.show_main()
		self.start_game()

	def start_game(self):
		self.state = 'GAME'
		self.hide_all()
		self.hud_frame.show()
		self.hud_score.show()
		self.hud_speed.show()
		self.hud_battery.show()
		self.hud_time.show()
		self.apply_mouse_state(False)

	def show_pause(self):
		self.state = 'PAUSE'
		self.hide_all()
		self.pause_menu.show()
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
