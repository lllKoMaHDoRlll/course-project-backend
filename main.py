from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, requests, random, re
from typing import TypedDict, List
from dotenv import load_dotenv

from utils.yandex_gpt import make_gpt_request, synthesize
from utils.database import database

from models.exercises import (
    ExerciseSentencesAnswer, 
    ExerciseSentencesData, 
    ExerciseWordsAnswer, 
    ExerciseWordsData,
    ExerciseSentenceDBData,
    ExerciseWordsDBData,
    ExerciseGramarDBData,
    ExerciseListeningDBData
)

load_dotenv()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://four-aliens-mate.loca.lt",
    "https://four-aliens-mate.loca.lt:4200",
    "https://tonolingo.ru"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/exercises/sentence")
async def get_exercise_sentences_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Составь предложение средней длины и его перевод на английский."
    )

    print(response)

    exercise = ExerciseSentenceDBData(
        id=0,
        sentence=response.split("—")[1].strip(),
        translation=response.split("—")[0].strip()
    )
    exercise_id = database.write_sentence_exercise(exercise)

    words = exercise["sentence"]
    random.shuffle(words)

    data = ExerciseSentencesData(
        id=exercise_id,
        translation=exercise["translation"],
        sentence=words
    )
    return data

@app.post("/exercises/sentence")
async def check_exercise_sentences_data(exercise_sentences_answer: ExerciseSentencesAnswer):
    exercise_data = database.get_sentence_exercise_by_id(exercise_sentences_answer.id)
    if not exercise_data: return {"result": False}
    result = exercise_data["sentence"] == exercise_sentences_answer.answer
    return {"result": result}

@app.get("/exercises/words")
async def get_exercise_words_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Придумай 10 слов на русском и напиши перевод к ним"
    )
    data = re.findall(r"\d+.[\s\*]*([а-яА-Я]+)[\s\*]*— ([a-zA-Z]+)", response)

    translations = [pair[0] for pair in data]
    words = [pair[1] for pair in data]

    exercise = ExerciseWordsDBData(
        id=0,
        words=words.copy(),
        translations=translations
    )
    exercise_id = database.write_words_exercise(exercise)

    random.shuffle(words)

    exercise_data = ExerciseWordsData(
        id=exercise_id,
        words=words,
        translations=exercise["translations"]
    )

    return exercise_data

@app.post("/exercises/words")
async def check_exercise_words_data(exercise_words_data: ExerciseWordsAnswer):
    exercise_data = database.get_words_exercise_by_id(exercise_words_data.id)
    if not exercise_data: return {"result": False}

    result = True
    for i in range(len(exercise_words_data.words)):
        if exercise_words_data.words[i] != exercise_data["words"][i]:
            result = False
            break
    
    return {"result": result}

@app.get("/exercises/listening")
async def get_exercise_listening_data():
    response = await make_gpt_request(
        "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
        "Придумай 3 слова на русском и напиши перевод к ним"
    )
    words = [[group for group in match if re.match("[a-zA-Z]+", group)][0] for match in re.findall(r"(\d+.\s+)?(?(1)([а-яА-Я]+\s+—\s+)?(?(2)([a-zA-Z]+)|([a-zA-Z]+))|(«)?(?(4)([a-zA-Z]+)»|([a-zA-Z]+)[.,]))", response)]

    exercise = ExerciseListeningDBData(
        id=0,
        words=words
    )
    exercise_id = database.write_listening_exercise(exercise)
    
    await synthesize(". ".join(exercise["words"]))
    return FileResponse(path="output.wav", filename=f"output_{exercise_id}.wav", media_type="audio/wav")

@app.get("/exercises/listening/{id}")
async def get_exercise_listening_data_by_id(id: int):
    return None
    result = database.get_listening_exercise_by_id(id)
    return {"result": result}

@app.get("/exercises/chain")
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

@app.get("/telegram/profile_photo")
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

@app.get("/achievements/types")
async def get_achievements_types():
    result = database.get_achievements_types()
    return {"result": result}
