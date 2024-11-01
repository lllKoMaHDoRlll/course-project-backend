from utils.database import Database
from models.achievements import ACHIEVEMENTS

def check_start_of_journey_completion(**kwargs) -> bool:
    try:
        return kwargs["total_entrances"] >= 1
    except KeyError: return False

def check_intrested_completion(**kwargs) -> bool:
    try:
        return kwargs["total_entrances"] >= 10
    except KeyError: return False

def check_guru_completion(**kwargs) -> bool:
    try:
        return kwargs["total_entrances"] >= 100
    except KeyError: return False

def check_sprinter_completion(**kwargs) -> bool:
    try:
        return kwargs["streak"] >= 5
    except KeyError: return False

def check_marathon_runner_completion(**kwargs) -> bool:
    try:
        return kwargs["streak"] >= 30
    except KeyError: return False

def check_foreigner_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_completion_count_total"] >= 10
    except KeyError: return False

def check_knowing_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_completion_count_total"] >= 100
    except KeyError: return False

def check_native_speaker_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_completion_count_total"] >= 300
    except KeyError: return False

def check_sentences_start_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_sentences_completion_count"] >= 3
    except KeyError: return False

def check_sentences_advanced_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_sentences_completion_count"] >= 10
    except KeyError: return False

def check_sentences_expert_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_sentences_completion_count"] >= 50
    except KeyError: return False

def check_words_start_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_words_completion_count"] >= 3
    except KeyError: return False

def check_words_advanced_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_words_completion_count"] >= 10
    except KeyError: return False

def check_words_expert_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_words_completion_count"] >= 50
    except KeyError: return False

def check_listening_start_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_listening_completion_count"] >= 3
    except KeyError: return False

def check_listening_advanced_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_listening_completion_count"] >= 10
    except KeyError: return False

def check_listening_expert_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_listening_completion_count"] >= 50
    except KeyError: return False

def check_gramar_start_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_gramar_completion_count"] >= 3
    except KeyError: return False

def check_gramar_advanced_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_gramar_completion_count"] >= 10
    except KeyError: return False

def check_gramar_expert_completion(**kwargs) -> bool:
    try:
        return kwargs["exercise_gramar_completion_count"] >= 50
    except KeyError: return False


ACHIEVEMENT_CHECKERS_MAP: dict = {
    ACHIEVEMENTS.START_OF_JOURNEY.name: check_start_of_journey_completion,
    ACHIEVEMENTS.INTRESTED.name: check_intrested_completion,
    ACHIEVEMENTS.GURU.name: check_guru_completion,
    ACHIEVEMENTS.SPRINTER.name: check_sprinter_completion,
    ACHIEVEMENTS.MARATHON_RUNNER.name: check_marathon_runner_completion,
    ACHIEVEMENTS.FOREIGNER.name: check_foreigner_completion,
    ACHIEVEMENTS.KNOWING.name: check_knowing_completion,
    ACHIEVEMENTS.NATIVE_SPEAKER.name: check_native_speaker_completion,
    ACHIEVEMENTS.SENTENCES_START.name: check_sentences_start_completion,
    ACHIEVEMENTS.SENTENCES_ADVANCED.name: check_sentences_advanced_completion,
    ACHIEVEMENTS.SENTENCES_EXPERT.name: check_sentences_expert_completion,
    ACHIEVEMENTS.WORDS_START.name: check_words_start_completion,
    ACHIEVEMENTS.WORDS_ADVANCED.name: check_words_advanced_completion,
    ACHIEVEMENTS.WORDS_EXPERT.name: check_words_expert_completion,
    ACHIEVEMENTS.LISTENING_START.name: check_listening_start_completion,
    ACHIEVEMENTS.LISTENING_ADVANCED.name: check_listening_advanced_completion,
    ACHIEVEMENTS.LISTENING_EXPERT.name: check_listening_expert_completion,
    ACHIEVEMENTS.GRAMAR_START.name: check_gramar_start_completion,
    ACHIEVEMENTS.GRAMAR_ADVANCED.name: check_gramar_advanced_completion,
    ACHIEVEMENTS.GRAMAR_EXPERT.name: check_gramar_expert_completion
}

def check_achievements_completion(database: Database, user_id: int, type_id: int = -1, **kwargs):
    uncompleted_achievements = [achievement for achievement in database.get_achievements_by_user_id(user_id, type_id) if not achievement["is_completed"]]
    completed_achievements = []
    for achievement in uncompleted_achievements:
        print(kwargs)
        if ACHIEVEMENT_CHECKERS_MAP[ACHIEVEMENTS(achievement["id"]).name](**kwargs):
            database.write_achievement_completion(user_id, achievement["id"])
            completed_achievements.append(achievement)
    return completed_achievements