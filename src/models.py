import os
from typing import TypedDict


type StrOrPath = str | os.PathLike[str]


class LevelCompleted(TypedDict):
	timestamp: str
	total_score: int


class Data(TypedDict):
	game_started: str
	level_completed: LevelCompleted
	drone_crashed: str
	game_closed: str


class AnalitycsEvent(TypedDict):
	name: str
	timestamp: str
	data: Data
