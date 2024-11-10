from main import app, database

from models.users import UserData, User

@app.post("/users")
async def create_or_update_user(user: UserData):
    database.write_or_update_user(User(id=user.user_id))