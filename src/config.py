from enum import Enum
import json
import os

from src.models import StrOrPath, JSONDict, JSONMapping


PATHS = {
	# 'assets': {
	# 	'models': {
	# 		'drone': 'assets/models/...',
	# 	},
	# 	'images': {
	# 		'...': '.../...'
	# 	},
	# },
	'conf': {
		'drone': 'conf/drone.json',
		'local': 'conf/local.json',
		'settings': 'conf/settings.json',
	},
	'data': {
		'analitycs': 'data/analitycs.json',
		'save': 'data/save.json',
	},
}


class Settings(Enum):
	LANGUAGE = 'language'
	SAVE_SLOT = 'save_slot'
	SAVE_SLOT_COUNT = 'save_slot_count'


class JSONConfig:
	def __init__(self, path: StrOrPath) -> None:
		self._path = path

		path_dirname = os.path.dirname(path)
		if not os.path.exists(path_dirname):
			os.makedirs(path_dirname)

	def dump(self, config: JSONMapping) -> None:
		with open(self._path, 'w', encoding='utf-8') as file:
			json.dump(config, file, ensure_ascii=False, indent=2)

	def load(self) -> JSONDict:
		with open(self._path, encoding='utf-8') as file:
			return json.load(file)


class SlotJSONConfig(JSONConfig):
	def __init__(
		self,
		path: StrOrPath,
		base_config: JSONMapping,
		settings: JSONConfig,
	) -> None:

		super().__init__(path)

		self._base_config = base_config
		self._settings = settings

		self._settings_body = settings.load()
		self._slot = str(self._settings_body[Settings.SAVE_SLOT.value])
		self._slot_count = self._settings_body[Settings.SAVE_SLOT_COUNT.value]

		self._initial_dump()

	def _initial_dump(self) -> None:
		if not os.path.exists(self._path):
			self.init_slots(self._slot_count, self._base_config)

	def init_slots(self, slot_count: int, base_config: JSONMapping) -> None:
		slots = {str(i): base_config for i in range(1, slot_count + 1)}
		super().dump(slots)

	def dump(self, config: JSONMapping) -> None:
		slots = self.load(all_=True)
		if self._slot not in slots:
			return

		slots[self._slot] = config
		super().dump(slots)

	def load(self, all_: bool = False) -> JSONDict:
		slots = super().load()
		if (not all_) and (self._slot in slots):
			return slots[self._slot]

		return slots


class Localization(SlotJSONConfig):
	def __init__(
		self,
		path: StrOrPath,
		base_config: JSONMapping,
		settings: JSONConfig,
	) -> None:

		super().__init__(path, base_config, settings)

	def load(self, all_: bool = False) -> JSONDict:
		localization = super().load()
		if all_:
			return localization

		language = self._settings.load()[Settings.LANGUAGE.value]
		if language in localization:
			return localization[language]

		raise KeyError(f'Language {language} not found')
