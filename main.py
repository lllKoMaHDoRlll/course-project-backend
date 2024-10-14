from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, random
from typing import TypedDict, List

from utils.yandex_gpt import make_gpt_request

class ExerciseSentencesAnswer(BaseModel):
    id: int
    answer: str

class ExerciseSentencesDBData(TypedDict):
    id: int
    sentence: str
    translation: str

class ExerciseSentencesData(TypedDict):
    id: int
    sentence: list[str]
    translation: str


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_sentences_mok: List[ExerciseSentencesDBData] = []

@app.get("/api/exercises/sentence")
async def get_exercise_sentences_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Составь предложение средней длины и его перевод на английский."
    )

    print(response)

    # сохранение ответа в бд
    db_data = ExerciseSentencesDBData(
        id=len(db_sentences_mok),
        sentence=response.split("—")[1].strip(),
        translation=response.split("—")[0].strip()
    )
    db_sentences_mok.append(db_data)
    print(db_sentences_mok)

    # Составление задания
    words = response.split("—")[1].strip().split(" ")
    random.shuffle(words)

    data = ExerciseSentencesData(
        id=len(db_sentences_mok) - 1,
        translation=response.split("—")[0].strip(),
        sentence=words
    )
    print(data)
    return data

@app.post("/api/exercises/sentence")
async def check_exercise_sentences_data(exercise_sentences_answer: ExerciseSentencesAnswer):
    exercise_data = db_sentences_mok[exercise_sentences_answer.id]
    result = exercise_data["sentence"] == exercise_sentences_answer.answer
    return {"result": result}

