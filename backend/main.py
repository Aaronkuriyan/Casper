from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import json, os, re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load local environment variables if they exist
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# FIX: Comprehensive CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://casper-seven.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
# Make sure "GEMINI_API_KEY" is set in your Render Environment Variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Memory setup
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
    return {"status": "CASPER online", "engine": "Gemini 1.5 Flash"}

@app.post("/chat")
async def chat(req: ChatRequest):
    memory_data = load_memory()
    all_memory = req.memory + memory_data["facts"] + memory_data["preferences"]
    
    # System Instruction for Gemini
    system_instruction = (
        f"You are CASPER, a personal AI assistant. Calm, precise, witty. "
        f"User info: {', '.join(all_memory) if all_memory else 'None'}. "
        f"Speak naturally, avoid markdown. Date: {datetime.now().strftime('%A, %d %B %Y')}."
    )

    # Convert frontend history to Gemini format (user/model)
    # We take the history EXCEPT the last message to start the session
    gemini_history = []
    for m in req.history[:-1]:
        role = "user" if m.role == "user" else "model"
        gemini_history.append({"role": role, "parts": [m.content]})

    try:
        # Start the chat session
        chat_session = model.start_chat(history=gemini_history)
        
        # Send the latest user message with system context
        prompt = f"{system_instruction}\n\nUser: {req.message}"
        response = chat_session.send_message(prompt)
        reply = response.text
        
        # Simple memory logic: Catch name introduction
        name_match = re.search(r"(?:my name is|i'm|call me)\s+([A-Z][a-z]+)", req.message, re.I)
        if name_match:
            entry = f"Name: {name_match.group(1)}"
            if entry not in memory_data["facts"]:
                memory_data["facts"].append(entry)
                save_memory(memory_data)
                
        return {"reply": reply}
        
    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")

# Ensure the app binds to the port Render expects
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)