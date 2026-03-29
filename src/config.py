import json
from collections.abc import Mapping
from typing import Any

from src.models import StrOrPath


class JSONConfig:
	def __init__(self, path: StrOrPath) -> None:
		self._path = path

	def dump(self, config: Mapping[str, Any]) -> None:
		with open(self._path, 'w', encoding='utf-8') as file:
			json.dump(config, file, ensure_ascii=False, indent=2)

	def load(self) -> dict[str, Any]:
		with open(self._path, encoding='utf-8') as file:
			return json.load(file)


class Localization(JSONConfig):
	def __init__(self, path: StrOrPath) -> None:
		super().__init__(path)

	def load(self, language: str | None = None) -> dict[str, Any]:
		localization = super().load()
		if language is None:
			return localization

		if language in localization:
			return localization[language]

		raise KeyError(f'Language {language} not found')
