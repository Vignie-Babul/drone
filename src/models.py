import os
from typing import TypedDict


type StrOrPath = str | os.PathLike[str]

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
