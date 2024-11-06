from mysql.connector import connect, MySQLConnection
from models.achievements import AchievementType, AchievementTypeProgress, Achievement
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
RUN_MODE = os.environ.get("RUN_MODE")

if RUN_MODE == "dev":
    import sshtunnel # type: ignore
    SSH_HOST=os.environ.get("SSH_HOST")
    SSH_USER=os.environ.get("SSH_USER")
    SSH_PASSWORD=os.environ.get("SSH_PASSWORD")

class Database:
    def __init__(self):
        port = 3306
        if RUN_MODE == "dev":
            self._tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_HOST, 22),
                ssh_username=SSH_USER,
                ssh_password=SSH_PASSWORD,
                remote_bind_address=("127.0.0.1", 3306)
            )
            self._tunnel.start()
            print(self._tunnel.tunnel_is_up)
            print(self._tunnel.local_bind_port)
            port = self._tunnel.local_bind_port
        self._connection = MySQLConnection(
            host="127.0.0.1",
            port=port,
            user=DB_USER,
            password=DB_PASSWORD,
            database="tonolingo"
        )
        self._cursor = self._connection.cursor()

    def get_achievements_by_user_id(self, user_id: int, achievement_type: int = -1) -> list[Achievement]:
        self._cursor.execute("""
                            SELECT 
                                a.id AS achievement_id, a.type_id, a.name, a.description, ca.SBT_received,
                                CASE 
                                    WHEN ca.tg_user_id IS NOT NULL THEN ca.tg_user_id
                                    ELSE NULL 
                                END
                            FROM 
                                achievements a
                            LEFT JOIN 
                                completed_achievements ca 
                            ON 
                                a.id = ca.achievement_id AND ca.tg_user_id = %s;
        """, (user_id,))
        result: list[Achievement] = []
        for (id_, type_id, name, description, SBT_received, tg_user_id) in self._cursor:
            if achievement_type == -1 or achievement_type == type_id:
                result.append({"id": id_, "name": name, "description": description, "type_id": type_id, "is_completed": tg_user_id is not None, "is_sbt_claimed": SBT_received if SBT_received is not None else False})
        return result
    
    def write_achievement_completion(self, user_id: int, achievement_id: int):
        self._cursor.execute("INSERT INTO completed_achievements (achievement_id, tg_user_id) VALUES (%s, %s);", (achievement_id, user_id))
        self._connection.commit()
    
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
    
    def get_exercises_completion_count(self, user_id: int, exercise_type: EXERCISES_TYPES | None = None) -> int:
        if exercise_type is None:
            self._cursor.execute("SELECT COUNT(id) as completed_exercises_count FROM completed_exercises WHERE tg_user_id = %s;", (user_id,))
        else:
            self._cursor.execute("SELECT COUNT(id) as completed_exercises_count FROM completed_exercises WHERE tg_user_id = %s AND exercise_type_id = %s;", (user_id, exercise_type.value))
        result = self._cursor.fetchone()[0]
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
                entrance_streak=result[2],
                total_entrances=result[3]
            )
        return None
    
    def get_user(self, user_id: int) -> User | None:
        self._cursor.execute("SELECT tg_user_id, wallet FROM users WHERE tg_user_id = %s;", (user_id,))
        user_data = self._cursor.fetchone()
        if user_data:
            return User(id=user_data[0], wallet=user_data[1])
        return None
            
    
    def update_user_total_stats(self, total_stats: TotalStats):
        self._cursor.execute("UPDATE total_stats SET last_entrance_date=%s, entrance_streak=%s, total_entrances=%s WHERE tg_user_id=%s", (total_stats["last_entrance_date"], total_stats["entrance_streak"], total_stats["total_entrances"], total_stats["user_id"]))
        self._connection.commit()
    
    def write_or_update_user(self, user: User): # TODO: if wallet is None then do not set the wallet column
        self._cursor.execute("SELECT (tg_user_id) from users WHERE tg_user_id=%s;", (user["id"],))
        self._cursor.fetchall()
        if self._cursor.rowcount == 1:
            self._cursor.execute("UPDATE users SET wallet=%s WHERE tg_user_id=%s;", (user["wallet"], user["id"]))
        else:
            self._cursor.execute("INSERT INTO users (tg_user_id) VALUES (%s);", (user["id"],))

            today = datetime.today().strftime("%Y-%m-%d")

            self._cursor.execute("INSERT INTO total_stats (tg_user_id, last_entrance_date, entrance_streak, total_entrances) VALUES (%s, %s, %s, %s);", (user["id"], today, 1, 1))
        self._connection.commit()

database = Database()
