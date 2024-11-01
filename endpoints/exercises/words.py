import re, random
from main import app, database

from utils.common import retry_on_exception
from utils.yandex_gpt import make_gpt_request
from utils.achievements import check_achievements_completion

from models.exercises import (
    ExerciseWordsDBData,
    ExerciseWordsData,
    ExerciseWordsAnswer,
    EXERCISES_TYPES
)

@app.get("/exercises/words")
@retry_on_exception()
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
async def check_exercise_words_data(exercise_words_data: ExerciseWordsAnswer, user_id: int):
    exercise_data = database.get_words_exercise_by_id(exercise_words_data.id)
    if not exercise_data: return {"result": False}

    result = True
    for i in range(len(exercise_words_data.words)):
        if exercise_words_data.words[i] != exercise_data["words"][i]:
            result = False
            break
    
    completed_achievements = []
    if result:
        database.complete_exercise(user_id, exercise_words_data.id, EXERCISES_TYPES.WORDS)
        completions_count_total = database.get_exercises_completion_count(user_id=user_id)
        completions_count = database.get_exercises_completion_count(user_id=user_id, exercise_type=EXERCISES_TYPES.WORDS)
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=1, exercise_completion_count_total=completions_count_total))
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=3, exercise_sentences_completion_count=completions_count))
    
    return {"result": result, "completed_achievements": completed_achievements}
