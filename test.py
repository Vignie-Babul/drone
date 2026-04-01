from pprint import pprint

from src.config import PATHS, Settings, JSONConfig, Localization, SlotJSONConfig
from src.data import Analytics, DataSave
from src.models import AnalyticsEvent
from src.utils import get_iso_datetime


def settings_test(settings: JSONConfig) -> None:
	settings.dump({
		Settings.LANGUAGE.value: 'en',
		Settings.SAVE_SLOT.value: 1,
		Settings.SAVE_SLOT_COUNT.value: 3,
	})
	pprint(settings.load())
	print()

def local_config_test(settings: JSONConfig, local: Localization) -> None:
	local.dump({
		'ru': {'foo': 'бар', 'hello_world': 'Привет, Мир!'},
		'en': {'foo': 'bar', 'hello_world': 'Hello! World!'},
	})
	pprint(local.load())
	print(local.load()['hello_world'])
	print()

def drone_config_test(settings: JSONConfig) -> None:
	drone = SlotJSONConfig(
		PATHS['conf']['drone'],
		{
			'max_speed': 0,
			'acceleration': 0,
			'rotation_speed': 0,
			'battery_life': 0,
			'obstacle_penalty': 0,
		},
		settings,
	)
	drone.dump({
		'max_speed': 1,
		'acceleration': 2,
		'rotation_speed': 3,
		'battery_life': 4,
		'obstacle_penalty': 5,
	})
	pprint(drone.load())
	print()

def analytics_test(analytics: Analytics) -> None:
	analytics_event_true: AnalyticsEvent = {
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

	analytics_event_false: AnalyticsEvent = {
		'name': 'event_' + get_iso_datetime(),
		'timestamp': get_iso_datetime(),
		'data': {
			'game_started': get_iso_datetime(),
			'game_closed': get_iso_datetime(),
			'status': False, # drone crashed
			'data': get_iso_datetime(),
		},
	}

	analytics.send(analytics_event_true, imitate=True)
	analytics.send(analytics_event_true, imitate=False)

	analytics.send(analytics_event_false, imitate=True)
	analytics.send(analytics_event_false, imitate=False)

def data_save_test(data_save: DataSave) -> None:
	pprint(data_save.load())
	data_save.dump(123, 4, 56789)
	pprint(data_save.load())


if __name__ == '__main__':
	settings = JSONConfig(PATHS['conf']['settings'])
	local = Localization(
		PATHS['conf']['local'],
		{'ru': {}, 'en': {}},
		settings,
	)
	analytics = Analytics(PATHS['data']['analytics'])
	data_save = DataSave(PATHS['data']['save'], settings)

	# settings_test(settings)
	# local_config_test(settings, local)
	# drone_config_test(settings)
	# analytics_test(analytics)
	# data_save_test(data_save)

