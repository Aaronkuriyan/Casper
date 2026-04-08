from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai  # Updated for 2026 SDK
import json, os, re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS setup for your Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://casper-seven.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the new Google GenAI Client
# Ensure GEMINI_API_KEY is set in your Render dashboard
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Local Memory Setup
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
        try:
            return json.loads(MEMORY_FILE.read_text())
        except:
            pass
    return {"facts": [], "preferences": [], "tasks": []}

def save_memory(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2))

@app.get("/")
def root():
    return {"status": "CASPER online", "engine": "Gemini 2.5 Flash"}

@app.post("/chat")
async def chat(req: ChatRequest):
    memory_data = load_memory()
    all_memory = req.memory + memory_data["facts"] + memory_data["preferences"]
    
    # System Instruction for the Assistant
    system_instruction = (
        f"You are CASPER, a personal AI assistant. Calm, precise, witty. "
        f"User info: {', '.join(all_memory) if all_memory else 'No previous data'}. "
        f"Speak naturally, avoid markdown. Today is {datetime.now().strftime('%A, %d %B %Y')}."
    )

    # Convert frontend history to the new 2026 SDK format
    # Note: role must be 'user' or 'model'
    contents = []
    for m in req.history:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})

    try:
        # Generate response using the 2.5 Flash model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={'system_instruction': system_instruction}
        )
        
        reply = response.text
        
        # Memory logic: detect name changes
        name_match = re.search(r"(?:my name is|i'm|call me)\s+([A-Z][a-z]+)", req.message, re.I)
        if name_match:
            entry = f"Name: {name_match.group(1)}"
            if entry not in memory_data["facts"]:
                memory_data["facts"].append(entry)
                save_memory(memory_data)
                
        return {"reply": reply}
        
    except Exception as e:
        print(f"Gemini 2.5 Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Render assigns a dynamic port; default to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)