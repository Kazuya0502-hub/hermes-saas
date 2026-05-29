import os
import requests
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ORGO_API_KEY = os.environ.get("ORGO_API_KEY")
BASE_URL = "https://www.orgo.ai/api"

# クライアントIDとVMの対応表（後でデータベースに移す）
CLIENT_VM_MAP = {
    "client_001": "75841a4f-c246-4c74-9fd4-f4158849e1de",
}

def get_headers():
    return {
        "Authorization": f"Bearer {ORGO_API_KEY}",
        "Content-Type": "application/json",
    }

def bash(computer_id, cmd):
    res = requests.post(
        f"{BASE_URL}/computers/{computer_id}/bash",
        headers=get_headers(),
        json={"command": cmd}
    )
    return res.json().get("output", "")

class Message(BaseModel):
    text: str
    client_id: str

@app.get("/")
def root():
    return {"status": "動いています"}

@app.post("/chat")
def chat(message: Message):
    computer_id = CLIENT_VM_MAP.get(message.client_id)
    if not computer_id:
        raise HTTPException(status_code=404, detail="クライアントが見つかりません")
    cmd = f"hermes -z '{message.text}' 2>&1 | tail -50"
    output = bash(computer_id, cmd)
    return {"reply": output}

@app.get("/status")
def status():
    return {"status": "ok", "orgo_key_set": bool(ORGO_API_KEY)}
