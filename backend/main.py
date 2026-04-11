from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai 
from supabase import create_client, Client
import json, os, re
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

# Initialize AI & Database Clients
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# We use a static ID since this is your personal assistant
USER_ID = "admin_aaron"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    memory: List[str] = []

def load_memory():
    """Fetches permanent memory from Supabase."""
    try:
        response = supabase.table("user_memory").select("*").eq("user_id", USER_ID).execute()
        if response.data:
            return response.data[0]
        else:
            # If no memory exists yet, create a blank slate in the database
            default_mem = {"user_id": USER_ID, "facts": [], "preferences": []}
            supabase.table("user_memory").insert(default_mem).execute()
            return default_mem
    except Exception as e:
        print(f"Supabase Load Error: {e}")
        return {"facts": [], "preferences": []}

def save_memory(data):
    """Saves updated memory back to Supabase."""
    try:
        supabase.table("user_memory").upsert(data).execute()
    except Exception as e:
        print(f"Supabase Save Error: {e}")

@app.get("/")
def root():
    return {"status": "CASPER online", "engine": "Gemini 2.5 Flash", "memory": "Supabase Active"}

@app.post("/chat")
async def chat(req: ChatRequest):
    # 1. Load permanent memory from the cloud
    memory_data = load_memory()
    
    # Safely handle lists just in case they are None
    db_facts = memory_data.get("facts") or []
    db_prefs = memory_data.get("preferences") or []
    
    all_memory = req.memory + db_facts + db_prefs
    
    # 2. System Instruction
    system_instruction = (
        f"You are CASPER, a personal AI assistant. Calm, precise, witty. "
        f"User info: {', '.join(all_memory) if all_memory else 'No previous data'}. "
        f"Speak naturally, avoid markdown. Today is {datetime.now().strftime('%A, %d %B %Y')}."
    )

    # 3. Format history for Gemini 2.5 SDK
    contents = []
    for m in req.history:
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})

    try:
        # 4. Generate Response
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={'system_instruction': system_instruction}
        )
        
        reply = response.text
        
        # 5. Simple Memory Logic: Catch name introductions or facts
        name_match = re.search(r"(?:my name is|i'm|call me)\s+([A-Z][a-z]+)", req.message, re.I)
        if name_match:
            new_name = name_match.group(1)
            entry = f"Name: {new_name}"
            if entry not in db_facts:
                db_facts.append(entry)
                memory_data["facts"] = db_facts
                save_memory(memory_data) # Send update to Supabase
                
        return {"reply": reply}
        
    except Exception as e:
        print(f"AI/DB Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)