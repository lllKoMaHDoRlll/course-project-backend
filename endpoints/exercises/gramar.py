from main import app, database

from utils.achievements import check_achievements_completion

from models.exercises import (
    ExerciseGramarData,
    ExerciseGramarAnswer,
    EXERCISES_TYPES
)


@app.get("/exercises/gramar")
async def get_exercise_gramar_data():
    exercise = database.get_random_gramar_exercise()
    #TODO: в БД увеличить размер аттрибута tasks
    exercise_data = ExerciseGramarData(
        id=exercise["id"],
        description=exercise["description"],
        tasks=exercise["tasks"]
    )

    return exercise_data

@app.post("/exercises/gramar")
async def check_exercise_gramar(answer: ExerciseGramarAnswer, user_id: int):
    exercise = database.get_gramar_exercise_by_id(answer.id)
    if not exercise: return None

    result = True
    for i in range(len(exercise["answers"])):
        if exercise["answers"][i] != answer.answers[i]:
            result = False
            break
    
    completed_achievements = []
    if result:
        database.complete_exercise(user_id, answer.id, EXERCISES_TYPES.GRAMAR)
        completions_count_total = database.get_exercises_completion_count(user_id=user_id)
        completions_count = database.get_exercises_completion_count(user_id=user_id, exercise_type=EXERCISES_TYPES.GRAMAR)
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=1, exercise_completion_count_total=completions_count_total))
        completed_achievements.extend(check_achievements_completion(database=database, user_id=user_id, type_id=5, exercise_sentences_completion_count=completions_count))
    
    return {"result": result, "completed_achievements": completed_achievements}
