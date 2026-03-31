import os
from collections.abc import Mapping
from typing import Any, TypedDict


type StrOrPath = str | os.PathLike[str]
type JSONDict = dict[str, Any]
type JSONMapping = Mapping[str, Any]

type DroneCrashed = str


class LevelCompleted(TypedDict):
	timestamp: str
	total_score: int


class Data(TypedDict):
	game_started: str
	game_closed: str
	status: bool
	data: LevelCompleted | DroneCrashed


class AnalitycsEvent(TypedDict):
	name: str
	timestamp: str
	data: Data
