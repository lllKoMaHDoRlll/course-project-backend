import re
from main import app, database
from fastapi.responses import FileResponse

from utils.common import retry_on_exception
from utils.yandex_gpt import make_gpt_request, synthesize
from utils.achievements import check_achievements_completion

from models.exercises import (
    ExerciseListeningDBData,
    ExerciseListeningAnswer,
    EXERCISES_TYPES
)

@app.get("/exercises/listening")
@retry_on_exception()
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

@app.post("/exercises/listening")
async def check_exercise_listening(exercise_listening_data: ExerciseListeningAnswer, user_id: int):
    exercise_data = database.get_listening_exercise_by_id(exercise_listening_data.id)
    if not exercise_data: return {"result": False}
    result = True
    for i in range(len(exercise_data["words"])):
        if exercise_data["words"][i] != exercise_listening_data.words[i]:
            result = False
            break
    
    completed_achievements = []
    if result:
        database.complete_exercise(user_id, exercise_listening_data.id, EXERCISES_TYPES.LISTENING)
        completions_count_total = database.get_exercises_completion_count(user_id=user_id)
        completions_count = database.get_exercises_completion_count(user_id=user_id, exercise_type=EXERCISES_TYPES.LISTENING)
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=1, exercise_completion_count_total=completions_count_total))
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=4, exercise_sentences_completion_count=completions_count))
    
    return {"result": result, "completed_achievements": completed_achievements}
