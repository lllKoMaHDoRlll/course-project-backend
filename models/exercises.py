from pydantic import BaseModel
from typing import TypedDict

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