import random
from main import app, database

from utils.yandex_gpt import make_gpt_request
from utils.common import retry_on_exception
from utils.achievements import check_achievements_completion

from models.exercises import (
    ExerciseSentenceDBData, 
    ExerciseSentencesData, 
    ExerciseSentencesAnswer, 
    EXERCISES_TYPES
)

@app.get("/exercises/sentence")
@retry_on_exception()
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

    words = exercise["sentence"].split()
    print(words)
    random.shuffle(words)

    data = ExerciseSentencesData(
        id=exercise_id,
        translation=exercise["translation"],
        sentence=words
    )
    return data

@app.post("/exercises/sentence")
async def check_exercise_sentences_data(exercise_sentences_answer: ExerciseSentencesAnswer, user_id: int):
    exercise_data = database.get_sentence_exercise_by_id(exercise_sentences_answer.id)
    if not exercise_data: return {"result": False}
    result = exercise_data["sentence"] == exercise_sentences_answer.answer
    completed_achievements = []
    if result:
        database.complete_exercise(user_id, exercise_sentences_answer.id, EXERCISES_TYPES.SENTENCE)
        completions_count_total = database.get_exercises_completion_count(user_id=user_id)
        completions_count = database.get_exercises_completion_count(user_id=user_id, exercise_type=EXERCISES_TYPES.SENTENCE)
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=1, exercise_completion_count_total=completions_count_total))
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=2, exercise_sentences_completion_count=completions_count))

    return {"result": result, "completed_achievements": completed_achievements}
