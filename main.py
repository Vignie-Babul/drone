from pprint import pprint

from src.config import PATHS, JSONConfig, Localization
from src.data import Analitycs, DataSave
from src.models import AnalitycsEvent
from src.utils import get_iso_datetime


def local_config_test() -> None:
	local = Localization(PATHS['conf']['local'])
	local.dump({
		'ru': {'foo': 'бар', 'hello_world': 'Привет, Мир!'},
		'en': {'foo': 'bar', 'hello_world': 'Hello! World!'},
	})
	pprint(local.load())
	pprint(local.load('ru'))
	pprint(local.load('en'))
	print(local.load('en')['hello_world'])
	print()

def drone_config_test() -> None:
	drone = JSONConfig(PATHS['conf']['drone'])
	drone.dump({
		'max_speed': 0,
		'acceleration': 0,
		'rotation_speed': 0,
		'battery_life': 0,
		'obstacle_penalty': 0,
	})
	pprint(drone.load())
	print()

def analitycs_test() -> None:
	analitycs_event_true: AnalitycsEvent = {
		'name': 'event_' + get_iso_datetime(),
		'timestamp': get_iso_datetime(),
		'data': {
			'game_started': get_iso_datetime(),
			'game_closed': get_iso_datetime(),
			'status': True, # level completed
			'data': {
				'timestamp': get_iso_datetime(),
				'total_score': 0,
			},
		},
	}

	analitycs_event_false: AnalitycsEvent = {
		'name': 'event_' + get_iso_datetime(),
		'timestamp': get_iso_datetime(),
		'data': {
			'game_started': get_iso_datetime(),
			'game_closed': get_iso_datetime(),
			'status': False, # drone crashed
			'data': get_iso_datetime(),
		},
	}

	analitycs_true = Analitycs(PATHS['data']['analitycs'], analitycs_event_true)
	analitycs_true.send(True)
	analitycs_true.send(False)

	analitycs_false = Analitycs(PATHS['data']['analitycs'], analitycs_event_false)
	analitycs_false.send(True)
	analitycs_false.send(False)

def data_save_test() -> None:
	data_save = DataSave(PATHS['data']['save'])
	print(data_save.load())
	data_save.dump()
	print(data_save.load())


if __name__ == '__main__':
	local_config_test()
	drone_config_test()
	analitycs_test()
	data_save_test()
