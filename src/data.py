import json
import os
import sys

from src.b64 import b64enc, b64dec
from src.config import Settings, JSONConfig
from src.models import AnalyticsEvent, StrOrPath, JSONDict
from src.utils import has_internet_connection


class Analytics:
	def __init__(self, path: StrOrPath) -> None:
		self._path = path

		path_dirname = os.path.dirname(path)
		if not os.path.exists(path_dirname):
			os.makedirs(path_dirname)

	def _send_to_server(self, analytics: AnalyticsEvent) -> None:
		print(analytics, file=sys.stderr)

	def _dump_to_file(self, analytics: AnalyticsEvent) -> None:
		with open(self._path, 'a', encoding='utf-8') as file:
			json.dump(analytics, file, ensure_ascii=False, indent=2)
			file.write('\n')

	def send(self, analytics: AnalyticsEvent, imitate: bool | None = None) -> None:
		if has_internet_connection(imitate=imitate):
			self._send_to_server(analytics)
			return

		self._dump_to_file(analytics)


class DataSave:
	def __init__(self, path: StrOrPath, settings: JSONConfig) -> None:
		self._path = path

		_settings = settings.load()
		self._slot = str(_settings[Settings.SAVE_SLOT.value])
		self._slot_count = _settings[Settings.SAVE_SLOT_COUNT.value]

		self._save = {
			'best_time': 0,
			'total_score': 0,
			'unlocked_levels': 0,
		}

		self._make_data_dir()
		self._init_dump()

	def _make_data_dir(self) -> None:
		path_dirname = os.path.dirname(self._path)
		if not os.path.exists(path_dirname):
			os.makedirs(path_dirname)

	def _init_dump(self) -> None:
		if os.path.exists(self._path):
			self._save = self.load()
		else:
			self._init_slots()

	def _init_slots(self) -> None:
		slots = {str(i): self._save for i in range(1, self._slot_count + 1)}
		with open(self._path, 'w', encoding='utf-8') as file:
			encrypted_json_data = b64enc(json.dumps(slots))
			file.write(encrypted_json_data.decode('utf-8'))

	def dump(
		self,
		best_time: int = 0,
		total_score: int = 0,
		unlocked_levels: int = 0,
	) -> None:

		self._save = {
			'best_time': best_time,
			'total_score': total_score,
			'unlocked_levels': unlocked_levels,
		}

		slots = self.load(all_=True)
		if self._slot not in slots:
			return

		slots[self._slot] = self._save
		with open(self._path, 'w', encoding='utf-8') as file:
			encrypted_json_data = b64enc(json.dumps(slots))
			file.write(encrypted_json_data.decode('utf-8'))

	def load(self, all_: bool = False) -> JSONDict:
		with open(self._path, encoding='utf-8') as file:
			file_bytes = file.read().encode('utf-8')
			slots = json.loads(b64dec(file_bytes))

			if (not all_) and (self._slot in slots):
				return slots[self._slot]

			return slots
