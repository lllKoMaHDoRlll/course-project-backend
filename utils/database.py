from mysql.connector import connect
from models.achievements import AchievementType, AchievementTypeProgress
from models.exercises import (
    ExerciseListeningDBData, 
    ExerciseWordsDBData, 
    ExerciseSentenceDBData,
    ExerciseGramarDBData,
    EXERCISES_TYPES
)
from models.users import TotalStats, User

import os, random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

class Database:
    def __init__(self):
        self._connection = connect(
            host="localhost",
            port=3306,
            user=DB_USER,
            password=DB_PASSWORD,
            database="tonolingo"
        )
        self._cursor = self._connection.cursor()
    
    def get_achievements_types_progresses(self, user_id: int) -> list[AchievementTypeProgress]:
        self._cursor.execute("SELECT * from achievements_types;")
        result: list[AchievementTypeProgress] = []
        achievements_types: list[AchievementType] = []
        for (id_, name) in self._cursor:
            achievements_types.append({"id": id_, "name": name})
        for achievement_type in achievements_types:
            print(str(achievement_type["id"]))
            self._cursor.execute("SELECT id, name, description FROM achievements WHERE type_id = %s ORDER BY id ASC;", (achievement_type["id"],))
            achievements = self._cursor.fetchall()
            achievement_type_progress: AchievementTypeProgress = {"id": achievement_type["id"], "name": achievement_type["name"], "total": self._cursor.rowcount, "completed": 0}
            
            for achievement in achievements:
                self._cursor.execute("SELECT (id) FROM completed_achievements WHERE tg_user_id = %s AND achievement_id = %s;", (user_id, achievement[0]))
                self._cursor.fetchone()
                if self._cursor.rowcount == 1:
                    achievement_type_progress["completed"] += 1
            result.append(achievement_type_progress)
        return result

    def get_listening_exercise_by_id(self, id: int) -> ExerciseListeningDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute("SELECT * from listening_exercises WHERE id = %s;", (id,))
        result = self._cursor.fetchone()
        print(result)
        if result: 
            return {"id": result[0], "words": result[1].split()}
        return None
    
    def write_listening_exercise(self, exercise: ExerciseListeningDBData) -> int:
        words = " ".join(exercise["words"])
        self._cursor.execute("INSERT INTO listening_exercises (words) VALUES (%s);", (words,))
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id

    def get_words_exercise_by_id(self, id: int) -> ExerciseWordsDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute("SELECT * from words_exercises WHERE id = %s;", (id,))
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "words": result[1].split(), "translations": result[2].split()}
        return None
    
    def write_words_exercise(self, exercise: ExerciseWordsDBData) -> int:
        words = " ".join(exercise["words"])
        translations = " ".join(exercise["translations"])
        self._cursor.execute("INSERT INTO words_exercises (words, translations) VALUES (%s, %s);", (words, translations))
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id

    def get_sentence_exercise_by_id(self, id: int) -> ExerciseSentenceDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute("SELECT * from sentence_exercises WHERE id = %s;", (id,))
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "sentence": result[1], "translation": result[2]}
        return None
    
    def write_sentence_exercise(self, exercise: ExerciseSentenceDBData) -> int:
        sentence = exercise["sentence"]
        translation = exercise["translation"]
        self._cursor.execute("INSERT INTO sentence_exercises (sentence, translation) VALUES (%s, %s);", (sentence, translation))
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id
    
    def get_random_gramar_exercise(self) -> ExerciseGramarDBData | None:
        self._cursor.execute("SELECT id from gramar_exercises;")
        ids = list(map(lambda t: t[0], self._cursor.fetchall()))
        random_id = random.choice(ids)
        self._cursor.execute("SELECT * from gramar_exercises WHERE id = %s;", (random_id,))
        result = self._cursor.fetchone()
        if result:
           return {"id": result[0], "description": result[1], "tasks": list(map(lambda task: task.split("%") , result[2].split("@"))), "answers": result[3].split("@")}
        return None
    
    def get_gramar_exercise_by_id(self, id: int) -> ExerciseGramarDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute("SELECT * from gramar_exercises WHERE id = %s;", (id,))
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "description": result[1], "tasks": list(map(lambda task: task.split("%") , result[2].split("@"))), "answers": result[3].split("@")}
        return None
    
    def get_completed_exercises_ids_by_user_id(self, exercise_type_id: int, user_id: int) -> list[int]:
        if not isinstance(user_id, int): return []
        self._cursor.execute("SELECT exercise_id from completed_exercises WHERE tg_user_id = %s AND exercise_type_id = %s;", (user_id, exercise_type_id))
        result = []
        for (exercise_id) in self._cursor:
            result.append(exercise_id)
        return result
    
    def write_gramar_exercise(self, exercise: ExerciseGramarDBData) -> int:
        description = exercise["description"]
        tasks = "@".join(map(lambda task: "%".join(task), exercise["tasks"]))
        answers = "@".join(exercise["answers"])
        self._cursor.execute("INSERT INTO gramar_exercises (description, tasks, answers) VALUES (%s, %s, %s);", (description, tasks, answers))
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id
    
    def complete_exercise(self, user_id: int, exercise_id: int, exercise_type_id: EXERCISES_TYPES):
        self._cursor.execute("INSERT INTO completed_exercises (tg_user_id, exercise_id, exercise_type_id) VALUES (%s, %s, %s);", (user_id, exercise_id, exercise_type_id.value))
        self._connection.commit()
    
    def get_user_total_stats(self, user_id: int) -> TotalStats | None:
        if not isinstance(user_id, int): return None
        self._cursor.execute("SELECT * from total_stats WHERE tg_user_id = %s;", (user_id,))
        result = self._cursor.fetchone()
        print(result)
        if result: 
            return TotalStats(
                user_id=result[0],
                last_entrance_date=result[1],
                entrance_streak=result[2]
            )
        return None
            
    
    def update_user_total_stats(self, total_stats: TotalStats):
        self._cursor.execute("UPDATE total_stats SET last_entrance_date=%s, entrance_streak=%s WHERE tg_user_id=%s", (total_stats["last_entrance_date"], total_stats["entrance_streak"], total_stats["user_id"]))
        self._connection.commit()
    
    def write_or_update_user(self, user: User):
        self._cursor.execute("SELECT (tg_user_id) from users WHERE tg_user_id=%s;", (user["id"],))
        self._cursor.fetchall()
        if self._cursor.rowcount == 1:
            self._cursor.execute("UPDATE users SET wallet=%s WHERE tg_user_id=%s;", (user["wallet"], user["id"]))
        else:
            self._cursor.execute("INSERT INTO users (tg_user_id) VALUES (%s);", (user["id"],))

            today = datetime.today().strftime("%Y-%m-%d")

            self._cursor.execute("INSERT INTO total_stats (tg_user_id, last_entrance_date, entrance_streak) VALUES (%s, %s, %s);", (user["id"], today, 1))
        self._connection.commit()

database = Database()
