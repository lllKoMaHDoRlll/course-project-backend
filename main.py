from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import os
from utils.database import database
from utils.ton import ton

load_dotenv()

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
RUN_MODE = os.environ.get("RUN_MODE")

def close_connections():
    database._connection.close()
    if RUN_MODE == "dev":
        database._tunnel.close()

root_path = "/api/"
if RUN_MODE == "dev":
        root_path = "/api"

app = FastAPI(root_path=root_path, on_shutdown=[close_connections]) # set root_path if on server with reverse proxy on /api/ path

origins = [
    "http://localhost",
    "http://localhost:4200",
    "https://tonolingo.ru"
]

if RUN_MODE == "dev":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

import endpoints