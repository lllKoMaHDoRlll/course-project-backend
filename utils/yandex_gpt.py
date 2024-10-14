import os, requests
from typing import TypedDict, Any

YAGPT_FOLDER_ID = os.environ.get("YAGPT_FOLDER_ID")
YAGPT_IAM_TOKEN = os.environ.get("YAGPT_IAM_TOKEN")

YAGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

async def make_gpt_request(premessage: str, message: str) -> str:
    data: dict[str, Any] = {}
    data["modelUri"] = f"gpt://{YAGPT_FOLDER_ID}/yandexgpt"
    data["completionOptions"] = {"temperature": 1, "maxTokens": 1000}

    data["messages"] = [
        {"role": "system", "text": premessage},
        {"role": "user", "text": message},
    ]

    response = requests.post(
        YAGPT_URL,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {YAGPT_IAM_TOKEN}"
        },
        json=data
    ).json()

    return response["result"]["alternatives"][0]["message"]["text"]

