import os, requests, wave
from typing import TypedDict, Any
from dotenv import load_dotenv

load_dotenv()

YAGPT_FOLDER_ID = os.environ.get("YAGPT_FOLDER_ID")
YAGPT_IAM_TOKEN = os.environ.get("YAGPT_IAM_TOKEN")

YAGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YASPEECHKIT_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

async def make_gpt_request(premessage: str, message: str) -> str:
    data: dict[str, Any] = {}
    data["modelUri"] = f"gpt://{YAGPT_FOLDER_ID}/yandexgpt"
    data["completionOptions"] = {"temperature": 1, "maxTokens": 1000}

    data["messages"] = [
        {"role": "system", "text": premessage},
        {"role": "user", "text": message},
    ]

    retries_count = 0
    while retries_count < 3:
        try:
            response = requests.post(
                YAGPT_URL,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {YAGPT_IAM_TOKEN}"
                },
                json=data
            ).json()

            return response["result"]["alternatives"][0]["message"]["text"]
        except Exception:
            retries_count += 1
            print("retrying...", retries_count)
            pass
    return ""
    

async def synthesize(text: str):
    data = {
        "text": text,
        "lang": 'en-US',
        "voice": "john",
        "folderId": YAGPT_FOLDER_ID,
        "format": "lpcm",
        "sampleRateHertz": 48000,
    }

    with requests.post(
        YASPEECHKIT_URL,
        headers={
            "Authorization": f"Bearer {YAGPT_IAM_TOKEN}"
        },
        data=data
    ) as resp:
        if resp.status_code != 200:
            raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

        with open("output.raw", "wb") as file:
            for chunk in resp.iter_content(chunk_size=None):
                file.write(chunk)
        
    with open("output.raw", "rb") as file:
        file_data = file.read()
        with wave.open("output.wav", "wb") as output_file:
            output_file.setnchannels(1)
            output_file.setsampwidth(2)
            output_file.setframerate(48000)
            output_file.writeframesraw(file_data)
