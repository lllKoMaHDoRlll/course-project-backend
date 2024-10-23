from pydantic import BaseModel
from typing import TypedDict
from enum import Enum

class ExerciseSentencesAnswer(BaseModel):
    id: int
    answer: str

class ExerciseSentencesData(TypedDict):
    id: int
    sentence: list[str]
    translation: str

class ExerciseWordsAnswer(BaseModel):
    id: int
    words: list[str]

class ExerciseWordsData(TypedDict):
    id: int
    words: list[str]
    translations: list[str]

class ExerciseGramarData(TypedDict):
    id: int
    description: str
    tasks: list[tuple[str, str]]

class ExerciseGramarAnswer(BaseModel):
    id: int
    answers: list[str]

class ExerciseListeningDBData(TypedDict):
    id: int
    words: list[str]

class ExerciseListeningAnswer(BaseModel):
    id: int
    words: list[str]

class ExerciseWordsDBData(TypedDict):
    id: int
    words: list[str]
    translations: list[str]

class ExerciseSentenceDBData(TypedDict):
    id: int
    sentence: str
    translation: str

class ExerciseGramarDBData(TypedDict):
    id: int
    description: str
    tasks: list[tuple[str, str]]
    answers: list[str]

class EXERCISES_TYPES(Enum):
    SENTENCE = 1
    WORDS = 2
    LISTENING = 3
    GRAMAR = 4
    CHAIN = 5
