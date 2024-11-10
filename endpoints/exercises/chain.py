import re
from main import app, database

from utils.yandex_gpt import make_gpt_request
from utils.common import retry_on_exception

@app.get("/exercises/chain")
async def get_exercise_chain_data(word: str | None = None):
    if word is None:
        response = await make_gpt_request(
            "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
            "Придумай случайное английское слово"
        )
        return {"result": response}
    else:
        response = (await make_gpt_request(
            "Ты будешь получать слово на английском, твоя задача сказать, реально ли существует такое слово или нет. Отвечай да или нет на русском.",
            f"{word}"
        )).lower()

        result = "да" in response or "yes" in response

        if result:
            response = await make_gpt_request(
                "Ты общаешься с программой, никак не дополняй свой ответ, предоставляй только ответ.",
                f"Придумай слово на английском, начинающееся на букву {word[-1]}"
            )
            new_word = re.findall(r"[a-zA-Z]+", response)
            print(new_word)
            return {"result": new_word}
        else:
            return None