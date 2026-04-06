from src.config import (
	PATHS,
	UI_TEXT,
	Settings,
	JSONConfig,
	Localization,
)
from src.data import Analytics, DataSave
from src.models import AnalyticsEvent
from src.utils import get_iso_datetime


class TestPractice1:
	settings = JSONConfig(PATHS['conf']['settings'])
	data_save = DataSave(PATHS['data']['save'], settings)
	local = Localization(
		PATHS['conf']['local'],
		UI_TEXT,
		settings,
	)
	analytics = Analytics(PATHS['data']['analytics'])

	def test_language_change(self) -> None:
		main_title = {
			'en': 'DRONE SIMULATOR',
			'ru': 'СИМУЛЯТОР ДРОНА',
		}

		current_language = self.settings.load()[Settings.LANGUAGE.value]
		assert self.local.load()['main_title'] == main_title[current_language]

	def test_data_save(self) -> None:
		current_data_save = self.data_save.load()

		self.data_save.dump(30, 500, 2)
		assert self.data_save.load() == {
			'best_time': 30,
			'total_score': 500,
			'unlocked_levels': 2,
		}

		self.data_save.dump(**current_data_save)

	def test_json_config(self) -> None:
		current_settings = self.settings.load()

		settings = self.settings.load()
		settings[Settings.SAVE_SLOT.value] = settings[Settings.SAVE_SLOT_COUNT.value]
		self.settings.dump(settings)

		settings = self.settings.load()
		assert settings[Settings.SAVE_SLOT.value] == settings[Settings.SAVE_SLOT_COUNT.value]

		self.settings.dump(current_settings)

	def test_analytics(self) -> None:
		analytics_event: AnalyticsEvent = {
			'name': 'event',
			'timestamp': get_iso_datetime(),
			'data': {
				'game_started': get_iso_datetime(),
				'game_closed': get_iso_datetime(),
				'status': False,
				'data': get_iso_datetime(),
			},
		}
		self.analytics.send(analytics_event, imitate=True)
