from mysql.connector import connect
from models.achievements import AchievementType
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
    
    def get_achievements_types(self) -> list[AchievementType]:
        self._cursor.execute("SELECT * from achievements_types;")
        result: list[AchievementType] = []
        for (id_, name) in self._cursor:
            result.append({"id": id_, "name": name})
        return result

    def get_listening_exercise_by_id(self, id: int) -> ExerciseListeningDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute(f"SELECT * from listening_exercises WHERE id = {id};")
        result = self._cursor.fetchone()
        print(result)
        if result: 
            return {"id": result[0], "words": result[1].split()}
        return None
    
    def get_completed_listening_exercises_ids_by_user_id(self, user_id: int) -> list[int]:
        if not isinstance(user_id, int): return []
        self._cursor.execute(f"SELECT exercise_id from completed_listening_exercises WHERE tg_user_id = {user_id};")
        result = []
        for (exercise_id) in self._cursor:
            result.append(exercise_id)
        return result
    
    def write_listening_exercise(self, exercise: ExerciseListeningDBData) -> int:
        words = " ".join(exercise["words"])
        self._cursor.execute(f'INSERT INTO listening_exercises (words) VALUES ("{words}");')
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id

    def get_words_exercise_by_id(self, id: int) -> ExerciseWordsDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute(f"SELECT * from words_exercises WHERE id = {id};")
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "words": result[1].split(), "translations": result[2].split()}
        return None
    
    def get_completed_words_exercises_ids_by_user_id(self, user_id: int) -> list[int]:
        if not isinstance(user_id, int): return []
        self._cursor.execute(f"SELECT exercise_id from completed_words_exercises WHERE tg_user_id = {user_id};")
        result = []
        for (exercise_id) in self._cursor:
            result.append(exercise_id)
        return result
    
    def write_words_exercise(self, exercise: ExerciseWordsDBData) -> int:
        words = " ".join(exercise["words"])
        translations = " ".join(exercise["translations"])
        self._cursor.execute(f'INSERT INTO words_exercises (words, translations) VALUES ("{words}", "{translations}");')
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id

    def get_sentence_exercise_by_id(self, id: int) -> ExerciseSentenceDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute(f"SELECT * from sentence_exercises WHERE id = {id};")
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "sentence": result[1], "translation": result[2]}
        return None

    def get_completed_sentence_exercises_ids_by_user_id(self, user_id: int) -> list[int]:
        if not isinstance(user_id, int): return []
        self._cursor.execute(f"SELECT exercise_id from completed_sentence_exercises WHERE tg_user_id = {user_id};")
        result = []
        for (exercise_id) in self._cursor:
            result.append(exercise_id)
        return result
    
    def write_sentence_exercise(self, exercise: ExerciseSentenceDBData) -> int:
        sentence = exercise["sentence"]
        translation = exercise["translation"]
        self._cursor.execute(f'INSERT INTO sentence_exercises (sentence, translation) VALUES ("{sentence}", "{translation}");')
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id
    
    def get_random_gramar_exercise(self) -> ExerciseGramarDBData | None:
        self._cursor.execute("SELECT id from gramar_exercises;")
        ids = list(map(lambda t: t[0], self._cursor.fetchall()))
        random_id = random.choice(ids)
        self._cursor.execute(f"SELECT * from gramar_exercises WHERE id = {random_id};")
        result = self._cursor.fetchone()
        if result:
           return {"id": result[0], "description": result[1], "tasks": list(map(lambda task: task.split("%") , result[2].split("@"))), "answers": result[3].split("@")}
        return None
    
    def get_gramar_exercise_by_id(self, id: int) -> ExerciseGramarDBData | None:
        if not isinstance(id, int): return None
        self._cursor.execute(f"SELECT * from gramar_exercises WHERE id = {id};")
        result = self._cursor.fetchone()
        if result:
            return {"id": result[0], "description": result[1], "tasks": list(map(lambda task: task.split("%") , result[2].split("@"))), "answers": result[3].split("@")}
        return None
    
    def get_completed_gramar_exercises_ids_by_user_id(self, user_id: int) -> list[int]:
        if not isinstance(user_id, int): return []
        self._cursor.execute(f"SELECT exercise_id from completed_gramar_exercises WHERE tg_user_id = {user_id};")
        result = []
        for (exercise_id) in self._cursor:
            result.append(exercise_id)
        return result
    
    def write_gramar_exercise(self, exercise: ExerciseGramarDBData) -> int:
        description = exercise["description"]
        tasks = "@".join(map(lambda task: "%".join(task), exercise["tasks"]))
        answers = "@".join(exercise["answers"])
        self._cursor.execute(f'INSERT INTO gramar_exercises (description, tasks, answers) VALUES ("{description}", "{tasks}", "{answers}");')
        self._connection.commit()
        last_insert_id = self._cursor.lastrowid
        return last_insert_id
    
    def complete_exercise(self, user_id: int, exercise_id: int, exercise_type_id: EXERCISES_TYPES):
        self._cursor.execute(f'INSERT INTO completed_exercises (tg_user_id, exercise_id, exercise_type_id) VALUES ({user_id}, {exercise_id}, {exercise_type_id});')
        self._connection.commit()
    
    def get_user_total_stats(self, user_id: int) -> TotalStats | None:
        if not isinstance(user_id, int): return None
        self._cursor.execute(f"SELECT * from total_stats WHERE tg_user_id = {user_id};")
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
        self._cursor.execute(f'UPDATE total_stas SET last_entrance_date={total_stats["last_entrance_date"]}, entrance_strak={total_stats["entrance_streak"]} WHERE tg_user_id={total_stats["user_id"]}')
        self._connection.commit()
    
    def write_or_update_user(self, user: User):
        self._cursor.execute(f'SELECT (tg_user_id, wallet) from users WHERE tg_user_id={user["id"]};')
        if self._cursor.rowcount == 1:
            self._cursor.execute(f'UPDATE users SET wallet="{user["wallet"]}" WHERE tg_user_id={user["id"]};')
        else:
            self._cursor.execute(f"INSERT INTO users (tg_user_id) VALUES ({user['id']});")

            today = datetime.today().strftime("%Y-%m-%d")

            self._cursor.execute(f"INSERT INTO total_stats (tg_user_id, last_entrance_date, entrance_streak, completed_tasks) VALUES ({user['id']}, {today}, 1, 0);")
        self._connection.commit()


    

database = Database()