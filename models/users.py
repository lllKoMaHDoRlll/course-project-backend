from typing import TypedDict
from pydantic import BaseModel

class TotalStats(TypedDict):
    user_id: int
    last_entrance_date: str
    entrance_streak: int
    total_entrances: int

class User(TypedDict):
    id: int
    wallet: str | None

class UserData(BaseModel):
    user_id: int
    wallet: str | None

