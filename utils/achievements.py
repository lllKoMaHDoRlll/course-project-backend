from utils.database import Database
from models.achievements import ACHIEVEMENTS

def is_more_than(value_name: str, bound: int):
    def inner(**kwargs):
        try:
            return kwargs[value_name] >= bound
        except KeyError: return False
    return inner

ACHIEVEMENT_CHECKERS_MAP: dict = {
    ACHIEVEMENTS.START_OF_JOURNEY.name: is_more_than("total_entrances", 1),# check_start_of_journey_completion,
    ACHIEVEMENTS.INTRESTED.name: is_more_than("total_entrances", 10),
    ACHIEVEMENTS.GURU.name: is_more_than("total_entrances", 100),
    ACHIEVEMENTS.SPRINTER.name: is_more_than("streak", 5),
    ACHIEVEMENTS.MARATHON_RUNNER.name: is_more_than("streak", 30),
    ACHIEVEMENTS.FOREIGNER.name: is_more_than("exercise_completion_count_total", 10),
    ACHIEVEMENTS.KNOWING.name: is_more_than("exercise_completion_count_total", 100),
    ACHIEVEMENTS.NATIVE_SPEAKER.name: is_more_than("exercise_completion_count_total", 300),
    ACHIEVEMENTS.SENTENCES_START.name: is_more_than("exercise_sentences_completion_count", 3),
    ACHIEVEMENTS.SENTENCES_ADVANCED.name: is_more_than("exercise_sentences_completion_count", 10),
    ACHIEVEMENTS.SENTENCES_EXPERT.name: is_more_than("exercise_sentences_completion_count", 50),
    ACHIEVEMENTS.WORDS_START.name: is_more_than("exercise_words_completion_count", 3),
    ACHIEVEMENTS.WORDS_ADVANCED.name: is_more_than("exercise_words_completion_count", 10),
    ACHIEVEMENTS.WORDS_EXPERT.name: is_more_than("exercise_words_completion_count", 50),
    ACHIEVEMENTS.LISTENING_START.name: is_more_than("exercise_listening_completion_count", 3),
    ACHIEVEMENTS.LISTENING_ADVANCED.name: is_more_than("exercise_listening_completion_count", 10),
    ACHIEVEMENTS.LISTENING_EXPERT.name: is_more_than("exercise_listening_completion_count", 50),
    ACHIEVEMENTS.GRAMAR_START.name: is_more_than("exercise_gramar_completion_count", 3),
    ACHIEVEMENTS.GRAMAR_ADVANCED.name: is_more_than("exercise_gramar_completion_count", 10),
    ACHIEVEMENTS.GRAMAR_EXPERT.name: is_more_than("exercise_gramar_completion_count", 50)
}

def check_achievements_completion(database: Database, user_id: int, type_id: int = -1, **kwargs):
    uncompleted_achievements = [achievement for achievement in database.get_achievements_by_user_id(user_id, type_id) if not achievement["is_completed"]]
    completed_achievements = []
    for achievement in uncompleted_achievements:
        if ACHIEVEMENT_CHECKERS_MAP[ACHIEVEMENTS(achievement["id"]).name](**kwargs):
            database.write_achievement_completion(user_id, achievement["id"])
            achievement["is_completed"] = True
            completed_achievements.append(achievement)
    return completed_achievements