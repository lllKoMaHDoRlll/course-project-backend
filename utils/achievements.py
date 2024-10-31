from utils.database import Database
from models.achievements import ACHIEVEMENTS

def check_start_of_journey_completion(**kwargs) -> bool:
    return kwargs["total_entrances"] >= 1

def check_intrested_completion(**kwargs) -> bool:
    return kwargs["total_entrances"] >= 10

def check_guru_completion(**kwargs) -> bool:
    return kwargs["total_entrances"] >= 100

def check_sprinter_completion(**kwargs) -> bool:
    return kwargs["streak"] >= 5

def check_marathon_runner_completion(**kwargs) -> bool:
    return kwargs["streak"] >= 30

def check_not_implemented(**kwargs) -> bool:
    return False


ACHIEVEMENT_CHECKERS_MAP: dict = {
    ACHIEVEMENTS.START_OF_JOURNEY.name: check_start_of_journey_completion,
    ACHIEVEMENTS.INTRESTED.name: check_intrested_completion,
    ACHIEVEMENTS.GURU.name: check_guru_completion,
    ACHIEVEMENTS.SPRINTER.name: check_sprinter_completion,
    ACHIEVEMENTS.MARATHON_RUNNER.name: check_marathon_runner_completion,
    
    ACHIEVEMENTS.FOREIGNER.name: check_not_implemented,
    ACHIEVEMENTS.KNOWING.name: check_not_implemented,
    ACHIEVEMENTS.NATIVE_SPEAKER.name: check_not_implemented,
    ACHIEVEMENTS.SENTENCES_START.name: check_not_implemented,
    ACHIEVEMENTS.SENTENCES_ADVANCED.name: check_not_implemented,
    ACHIEVEMENTS.SENTENCES_EXPERT.name: check_not_implemented,
    ACHIEVEMENTS.WORDS_START.name: check_not_implemented,
    ACHIEVEMENTS.WORDS_ADVANCED.name: check_not_implemented,
    ACHIEVEMENTS.WORDS_EXPERT.name: check_not_implemented,
    ACHIEVEMENTS.LISTENING_START.name: check_not_implemented,
    ACHIEVEMENTS.LISTENING_ADVANCED.name: check_not_implemented,
    ACHIEVEMENTS.LISTENING_EXPERT.name: check_not_implemented,
    ACHIEVEMENTS.GRAMAR_START.name: check_not_implemented,
    ACHIEVEMENTS.GRAMAR_ADVANCED.name: check_not_implemented,
    ACHIEVEMENTS.GRAMAR_EXPERT.name: check_not_implemented
}

def check_achievements_completion(database: Database, user_id: int, type_id: int = -1, **kwargs):
    uncompleted_achievements = [achievement for achievement in database.get_achievements_by_user_id(user_id, type_id) if not achievement["is_completed"]]
    completed_achievements = []
    for achievement in uncompleted_achievements:
        if ACHIEVEMENT_CHECKERS_MAP[ACHIEVEMENTS(achievement["id"]).name](**kwargs):
            database.write_achievement_completion(user_id, achievement["id"])
            completed_achievements.append(achievement)
    return completed_achievements