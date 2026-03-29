from src.data import Analitycs, DataSave
from src.utils import get_iso_datetime


PATHS = {
	'local_conf': 'conf/local.json',
	'drone_conf': 'conf/drone.json',
	'analitycs': 'data/analitycs.json',
	'data_save': 'data/save.json',
}


def analitycs_test() -> None:
	analitycs = Analitycs(
		PATHS['analitycs'],
		{
			'name': 'event_' + get_iso_datetime(),
			'timestamp': get_iso_datetime(),
			'data': {
				'game_started': get_iso_datetime(),
				'level_completed': {
					'timestamp': get_iso_datetime(),
					'total_score': 0,
				},
				'drone_crashed': get_iso_datetime(),
				'game_closed': get_iso_datetime(),
			},
		}
	)
	analitycs.send(True)
	analitycs.send(False)

def data_save_test() -> None:
	data_save = DataSave(PATHS['data_save'])
	print(data_save.load())
	data_save.dump()
	print(data_save.load())


if __name__ == '__main__':
	analitycs_test()
	data_save_test()
