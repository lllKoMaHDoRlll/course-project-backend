from mysql.connector import connect
from models.achievements import AchievementType
import os

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

database = Database()