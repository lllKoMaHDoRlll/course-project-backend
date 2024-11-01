import requests
from main import app, TG_BOT_TOKEN
from fastapi.responses import FileResponse

@app.get("/telegram/profile_photo")
async def get_telegram_user_profile_photo(user_id: int):
    print(1)
    response = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUserProfilePhotos?user_id={user_id}").json()
    print(response)
    profile_photo_id = response["result"]["photos"][-1][-1]["file_id"]
    response = requests.get(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile?file_id={profile_photo_id}").json()
    print(response)
    profile_photo_path = response["result"]["file_path"]
    response = requests.get(f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{profile_photo_path}")
    with open("profile_photo.jpg", "wb") as file:
        file.write(response.content)
    print("photo obtained")
    return FileResponse("profile_photo.jpg", media_type="image/jpg")