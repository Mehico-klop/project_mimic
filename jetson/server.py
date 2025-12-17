from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
from player import play_sequence

app = FastAPI()

app.mount("/", StaticFiles(directory="../web", html=True), name="web")

SEQUENCE_FILE = "sequences/mission.json"


@app.post("/api/upload_sequence")
async def upload_sequence(data: dict):
    sequence = data["sequence"]

    # простая валидация
    if len(sequence) != 10:
        return {"error": "Must be 10 rows"}

    with open(SEQUENCE_FILE, "w") as f:
        json.dump(sequence, f)

    return {"status": "saved"}


@app.post("/api/play")
async def play():
    play_sequence(SEQUENCE_FILE)
    return {"status": "playing"}
