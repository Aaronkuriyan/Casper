from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import anthropic
import json, os, re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MEMORY_FILE = Path("memory/jarvis_memory.json")
MEMORY_FILE.parent.mkdir(exist_ok=True)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    memory: List[str] = []

def load_memory():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return {"facts": [], "preferences": [], "tasks": []}

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

@app.get("/")
def root():
    return {"status": "JARVIS online"}

@app.post("/chat")
async def chat(req: ChatRequest):
    memory_data = load_memory()
    all_memory = req.memory + memory_data["facts"] + memory_data["preferences"]
    system_prompt = f"""You are JARVIS, a personal AI assistant like Iron Man's JARVIS. Calm, precise, witty. {f"User info: {', '.join(all_memory)}." if all_memory else ""} Speak naturally, no markdown. Date: {datetime.now().strftime("%A, %d %B %Y, %H:%M")}."""
    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})
    try:
        response = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, system=system_prompt, messages=messages)
        reply = response.content[0].text
        name_match = re.search(r"(?:my name is|i'm|call me)\s+([A-Z][a-z]+)", req.message, re.I)
        if name_match:
            entry = f"Name: {name_match.group(1)}"
            if entry not in memory_data["facts"]:
                memory_data["facts"].append(entry)
                save_memory(memory_data)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))