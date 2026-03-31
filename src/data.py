import json
import os
import sys

from src.b64 import b64enc, b64dec
from src.models import StrOrPath, AnalitycsEvent
from src.utils import has_internet_connection


class Analitycs:
	def __init__(self, path: StrOrPath, analitycs: AnalitycsEvent) -> None:
		self._path = path
		self._analitycs = analitycs

		path_dirname = os.path.dirname(path)
		if not os.path.exists(path_dirname):
			os.makedirs(path_dirname)

	def _send_to_server(self) -> None:
		# send to the stderr to imitate sending to a server
		print(self._analitycs, file=sys.stderr)

	def _dump_to_file(self) -> None:
		with open(self._path, 'a', encoding='utf-8') as file:
			json.dump(self._analitycs, file, ensure_ascii=False, indent=2)
			file.write('\n')

	def send(self, imitate: bool | None = None) -> None:
		if has_internet_connection(imitate=imitate):
			self._send_to_server()
			return

		self._dump_to_file()


class DataSave:
	def __init__(self, path: StrOrPath) -> None:
		self._path = path

		self._data = {
			'best_time': 0,
			'total_score': 0,
			'unlocked_levels': 0,
			'version': 0,
		}

		path_dirname = os.path.dirname(path)
		if not os.path.exists(path_dirname):
			os.makedirs(path_dirname)

		if os.path.exists(path):
			self._data = self.load()
		else:
			self.dump()

	def dump(
		self,
		best_time: int = 0,
		total_score: int = 0,
		unlocked_levels: int = 0,
	) -> None:

		self._data = {
			'best_time': best_time,
			'total_score': total_score,
			'unlocked_levels': unlocked_levels,
			'version': self._data['version'] + 1,
		}

		with open(self._path, 'w', encoding='utf-8') as file:
			encrypted_json_data = b64enc(json.dumps(self._data))
			file.write(encrypted_json_data.decode('utf-8'))

	def load(self) -> dict:
		with open(self._path, encoding='utf-8') as file:
			file_bytes = file.read().encode('utf-8')
			return json.loads(b64dec(file_bytes))

