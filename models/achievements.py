from typing import TypedDict
from enum import Enum


class Achievement(TypedDict):
    id: int
    name: str
    description: str
    type_id: int
    is_completed: bool
    is_sbt_claimed: bool

class AchievementType(TypedDict):
    id: int
    name: str

class AchievementTypeProgress(TypedDict):
    id: int
    name: str
    completed: int
    total: int

class ACHIEVEMENTS(Enum):
    START_OF_JOURNEY = 1
    INTRESTED = 2
    GURU = 3
    SPRINTER = 4
    MARATHON_RUNNER = 5
    FOREIGNER = 6
    KNOWING = 7
    NATIVE_SPEAKER = 8
    SENTENCES_START = 9
    SENTENCES_ADVANCED = 10
    SENTENCES_EXPERT = 11
    WORDS_START = 12
    WORDS_ADVANCED = 13
    WORDS_EXPERT = 14
    LISTENING_START = 15
    LISTENING_ADVANCED = 16
    LISTENING_EXPERT = 17
    GRAMAR_START = 18
    GRAMAR_ADVANCED = 19
    GRAMAR_EXPERT = 20
