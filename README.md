# VR drone simulator

## Документация модулей

### `b64.py`
**Назначение:** модуль кодирования/декодирования строк в Base64.

**Подключение:**
```py
from src.b64 import b64enc, b64dec
```

**Примеры использования:**
- Кодирование:
```py
>>> b64enc('Hello, World!')
b'SGVsbG8sIFdvcmxkIQ=='
```

- Декодирование:
```py
>>> b64dec(b'SGVsbG8sIFdvcmxkIQ==')
'Hello, World!'
```

**Настройки:**
- `encoding='ascii'` - кодировка для кодирования/декодирования строки из байт и обратно. Поддерживает `'ascii'`, `'utf-8'` и `'utf-16'`.

---

### `config.py`
**Назначение:** модуль управления конфигурацией программы.

**Подключение:**
```py
from src.config import (
	PATH,
	Settings,
	JSONConfig,
	SlotJSONConfig,
	Localization,
)
```

**Примеры использования:**
- Получение пути к конфигу:
```py
>>> PATHS['conf']['settings']
'conf/settings.json'
```

- Получение названия ключа конфига настроек:
```py
>>> Settings.LANGUAGE.value
'language'
```

- Инициализация класса `JSONConfig` (менеджер JSON конфигов) и загрузка конфига:
```py
>>> settings = JSONConfig(PATHS['conf']['settings'])
>>> settings.load()
{
  "language": "en",
  "save_slot": 1,
  "save_slot_count": 3
}
```
- Инициализация класса `SlotJSONConfig` (менеджер JSON конфигов со слотами) и загрузка конфига текущего слота:
```py
>>> drone = SlotJSONConfig(
... 	PATHS['conf']['drone'],
... 	{
... 		'max_speed': 15,
... 		'acceleration': 5,
... 		'rotation_speed': 90,
... 		'battery_life': 300,
... 		'obstacle_penalty': 50,
... 	},
... 	settings,
... )
>>> drone.load()
{
  "max_speed": 15,
  "acceleration": 5,
  "rotation_speed": 90,
  "battery_life": 300,
  "obstacle_penalty": 50
}
```

- Инициализация класса `Localization` (менеджер локализации) и загрузка локализации выбранного языка в текущем слоте:
```py
>>> local = Localization(
... 	PATHS['conf']['local'],
... 	{'ru': {}, 'en': {}},
... 	settings,
... )
>>> local.load()
{
  "foo": "bar",
  "hello_world": "Hello! World!"
}
```
**Настройки:**
- `path: StrOrPath` - путь к файлу;
- `base_config: JSONMapping` - базовый конфиг;
- `settings: JSONConfig` - экземпляр класса конфига настроек.

---

### `data.py`
**Назначение:** модуль управления данными.

**Подключение:**
```py
from src.data import Analytics, DataSave
```

**Примеры использования:**
- Инициализация класса `Analytics` (менеджер аналитики) и отправка аналитики:
```py
>>> analytics = Analytics(PATHS['data']['analytics'])
>>> analytics.send({
... 	'name': 'event_' + get_iso_datetime(),
... 	'timestamp': get_iso_datetime(),
... 	'data': {
... 		'game_started': get_iso_datetime(),
... 		'game_closed': get_iso_datetime(),
... 		'status': True, # level completed
... 		'data': {
... 			'timestamp': get_iso_datetime(),
... 			'total_score': 0,
... 		},
... 	},
... }, imitate=True)
```

- Инициализация класса `DataSave` (менеджер сохранений), запись/чтение сохранения в текущем слоте:
```py
>>> data_save = DataSave(PATHS['data']['save'], settings)
>>> data_save.dump(
	best_time=25,
	total_score=4000,
	unlocked_levels=4,
)
>>> data_save.load()
{
  'best_time': 25,
  'total_score': 4500,
  'unlocked_levels': 4
}
```

**Настройки:**
- `path: StrOrPath` - путь к файлу;
- `base_config: JSONMapping` - базовый конфиг;
- `settings: JSONConfig` - экземпляр класса конфига настроек;
- `imitate: bool = False` - имитирование подключения к интернету.

---

### `models.py`
**Назначение:** модуль моделей (типов данных). Используется для аннотации типов.

**Подключение:**
```py
from src.models import (
	StrOrPath,
	JSONDict,
	JSONMapping,
	AnalyticsEvent,
)
```

**Примеры использования:**
- Аннотации типов:
```py
class SlotJSONConfig(JSONConfig):
	def __init__(
		self,
		path: StrOrPath,
		base_config: JSONMapping,
		settings: JSONConfig,
	) -> None:

		...
```

```py
class Analytics:

	...

	def send(self, analytics: AnalyticsEvent, ...) -> None:
		...
```

```py
analytics_event: AnalyticsEvent = {
	...
}

analytics.send(analytics_event)
```

**Настройки:** *отсутствуют.*

---

### `utils.py`
**Назначение:** модуль одиночных функций-утилит.

**Подключение:**
```py
from src.utils import (
	get_iso_datetime,
	has_internet_connection,
)
```

**Примеры использования:**
- Получение текущей даты и времени (формат ISO 8601):
```py
analytics.send({
	'name': 'event_' + get_iso_datetime(),

	...
})
```

- Проверка наличия подключения к интернету:
```py
class Analytics:

	...

	def send(self, ...) -> None:
		if has_internet_connection(imitate=imitate):
			...
	
		...
```

**Настройки:**
- `imitate: bool = False` - имитирование подключения к интернету.
