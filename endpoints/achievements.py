from datetime import datetime, timedelta
from main import app, database, ton

from utils.achievements import check_achievements_completion

from models.users import User

@app.get("/achievements/types")
async def get_achievements_types_progresses(user_id: int):
    result = database.get_achievements_types_progresses(user_id)
    return {"result": result}

@app.get("/achievements")
async def get_achievements(user_id: int, type_id: int):
    result = database.get_achievements_by_user_id(user_id, type_id)
    return {"result": result}

@app.post("/achievements/visits")
async def update_visit_status(user_id: int):
    database.write_or_update_user(User(id=user_id, wallet=None))
    user_stats = database.get_user_total_stats(user_id)
    if user_stats:
        print(user_stats)
        today = datetime.today().strftime("%Y-%m-%d")
        yesterday = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d")

        streak = user_stats["entrance_streak"]
        total_entrances = user_stats["total_entrances"]

        if str(user_stats["last_entrance_date"]) == str(yesterday):
            streak += 1
            total_entrances += 1
        elif str(user_stats["last_entrance_date"]) != str(today):
            print("reset streak")
            streak = 1
            total_entrances += 1

        user_stats["last_entrance_date"] = today
        user_stats["entrance_streak"] = streak
        user_stats["total_entrances"] = total_entrances
        database.update_user_total_stats(user_stats)

        completed_achievements = check_achievements_completion(database, user_id, 1, total_entrances=total_entrances, streak=streak)

        result = {"completed_achievements": completed_achievements}
        return result
    
@app.post("/achievements/sbt")
async def claim_sbt(user_id: int, achievement_id: int):

    user_achievements = database.get_achievements_by_user_id(user_id)
    user = database.get_user(user_id)
    if user is None:
        return {"error": "user not found"}
    
    for achievement in user_achievements:
        if achievement["id"] == achievement_id and achievement["is_completed"]:
            required_achievement = achievement
    
    print(user)
    
    if required_achievement["is_completed"] and not required_achievement["is_sbt_claimed"]:
        if user["wallet"] is not None:
            tx_hash = await ton.mint_sbt(
                user["wallet"], 
                required_achievement["name"], 
                required_achievement["description"],
                ton.SBTS_IMAGE_PATH.format(required_achievement["id"]),
                []
            )
            print(tx_hash)