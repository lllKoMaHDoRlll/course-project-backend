from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, requests, random, re
from typing import TypedDict, List

from utils.yandex_gpt import make_gpt_request, synthesize

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

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

class ExerciseWordsAnswer(BaseModel):
    id: int
    words: list[str]

class ExerciseWordsData(TypedDict):
    id: int
    words: list[str]
    translations: list[str]

class ExerciseWordsDBData(TypedDict):
    id: int
    words: list[str]
    translations: list[str]

class ExerciseListeningDBData(TypedDict):
    id: int
    words: str


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://four-aliens-mate.loca.lt",
    "https://four-aliens-mate.loca.lt:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

db_sentences_mok: List[ExerciseSentencesDBData] = []
db_words_mok: List[ExerciseWordsDBData] = []
db_listening_mok: List[ExerciseListeningDBData] = []

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

@app.get("/api/exercises/words")
async def get_exercise_words_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Придумай 10 слов на русском и напиши перевод к ним"
    )
    print(response)
    data = re.findall(r"\d+.[\s\*]*([а-яА-Я]+)[\s\*]*— ([a-zA-Z]+)", response)
    print(data)

    translations = [pair[0] for pair in data]
    words = [pair[1] for pair in data]

    db_data = ExerciseWordsDBData(
        id=len(db_words_mok),
        words=words.copy(),
        translations=translations
    )
    db_words_mok.append(db_data)
    print(db_words_mok)

    random.shuffle(words)

    exercise_data = ExerciseWordsData(
        id=len(db_words_mok) - 1,
        words=words,
        translations=translations
    )

    return exercise_data

@app.post("/api/exercises/words")
async def check_exercise_words_data(exercise_words_data: ExerciseWordsAnswer):
    words_data = db_words_mok[exercise_words_data.id]["words"]
    result = True
    for i in range(len(exercise_words_data.words)):
        if exercise_words_data.words[i] != words_data[i]:
            result = False
            break
    
    return {"result": result}

@app.get("/api/exercises/listening")
async def get_exercise_listening_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Придумай 3 слова на русском и напиши перевод к ним"
    )
    print(response)
    print(re.findall(r"(\d+.\s+)?(?(1)([а-яА-Я]+\s+—\s+)?(?(2)([a-zA-Z]+)|([a-zA-Z]+))|(«)?(?(4)([a-zA-Z]+)»|([a-zA-Z]+)[.,]))", response))
    words = [[group for group in match if re.match("[a-zA-Z]+", group)][0] for match in re.findall(r"(\d+.\s+)?(?(1)([а-яА-Я]+\s+—\s+)?(?(2)([a-zA-Z]+)|([a-zA-Z]+))|(«)?(?(4)([a-zA-Z]+)»|([a-zA-Z]+)[.,]))", response)]
    print(words)

    db_data = ExerciseListeningDBData(
        id=len(db_listening_mok),
        words=words
    )
    db_listening_mok.append(db_data)
    
    await synthesize(". ".join(words))
    return FileResponse(path="output.wav", filename=f"output_{len(db_listening_mok) - 1}.wav", media_type="audio/wav")

@app.get("/api/exercises/chain")
async def get_exercise_chain_data(word: str | None = None):
    if word is None:
        response = await make_gpt_request(
            "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
            "Придумай случайное английское слово"
        )
        return {"result": response}
    else:
        response = (await make_gpt_request(
            "Ты будешь получать слово на английском, твоя задача сказать, реально ли существует такое слово или нет. Отвечай да или нет на русском.",
            f"{word}"
        )).lower()

        result = "да" in response or "yes" in response

        if result:
            response = await make_gpt_request(
                "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
                f"Придумай слово на английском, начинающееся на букву {word[-1]}"
            )
            new_word = re.findall(r"[a-zA-Z]+", response)
            print(new_word)
            return {"result": new_word}
        else:
            return None

@app.get("/api/telegram/profile_photo")
async def get_telegram_user_profile_photo(user_id: int):
    print(1)
    response = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUserProfilePhotos?user_id={user_id}").json()
    print(response)
    profile_photo_id = response["result"]["photos"][-1][-1]["file_id"]
    response = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={profile_photo_id}").json()
    print(response)
    profile_photo_path = response["result"]["file_path"]
    response = requests.get(f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{profile_photo_path}")
    with open("profile_photo.jpg", "wb") as file:
        file.write(response.content)
    print("photo obtained")
    return FileResponse("profile_photo.jpg", media_type="image/jpg")


