from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types # Added to properly format history for tools
from supabase import create_client, Client
import json, os, re, requests # Added requests for our tool
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://casper-seven.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_KEY")
)

USER_ID = "admin_aaron"

# ==========================================
# 🛠️ CASPER'S REAL-WORLD TOOLS
# ==========================================
def get_weather(location: str) -> str:
    """Gets the current real-time weather for a specific city or location."""
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return "System Error: Weather API key is missing from the environment."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return f"Could not find weather data for {location}."
        
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        return f"The current weather in {location} is {temp}°C with {desc}."
    except Exception as e:
        return f"Failed to fetch weather: {str(e)}"

# You can add more tools here later (like get_news, check_crypto_price, etc.)
casper_tools = [get_weather] 

# ==========================================
# CORE LOGIC
# ==========================================

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []
    memory: List[str] = []

def load_memory():
    try:
        response = supabase.table("user_memory").select("*").eq("user_id", USER_ID).execute()
        if response.data:
            return response.data[0]
        default_mem = {"user_id": USER_ID, "facts": [], "preferences": []}
        supabase.table("user_memory").insert(default_mem).execute()
        return default_mem
    except:
        return {"facts": [], "preferences": []}

def save_memory(data):
    try:
        supabase.table("user_memory").upsert(data).execute()
    except Exception as e:
        print(f"Supabase Save Error: {e}")

@app.get("/")
def root():
    return {"status": "CASPER online", "engine": "Gemini 2.5 Flash", "tools": "Active"}

@app.post("/chat")
async def chat(req: ChatRequest):
    memory_data = load_memory()
    db_facts = memory_data.get("facts") or []
    db_prefs = memory_data.get("preferences") or []
    all_memory = req.memory + db_facts + db_prefs
    
    system_instruction = (
        f"You are CASPER, a personal AI assistant. Calm, precise, witty. "
        f"User info: {', '.join(all_memory) if all_memory else 'No previous data'}. "
        f"Speak naturally, avoid markdown. Today is {datetime.now().strftime('%A, %d %B %Y')}."
    )

    # Convert history into the strict format the SDK needs for tool execution
    history_contents = []
    # We take everything EXCEPT the last message to start the session
    for m in req.history[:-1]:
        role = "user" if m.role == "user" else "model"
        history_contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=m.content)])
        )

    try:
        # We use 'chats.create' instead of 'models.generate_content'
        # This tells the SDK to automatically handle the function calling loop for us!
        chat_session = gemini_client.chats.create(
            model="gemini-2.5-flash",
            history=history_contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=casper_tools, # This is where we hand Casper his tools!
                temperature=0.7
            )
        )
        
        # Send the latest message
        response = chat_session.send_message(req.message)
        reply = response.text
        
        name_match = re.search(r"(?:my name is|i'm|call me)\s+([A-Z][a-z]+)", req.message, re.I)
        if name_match:
            entry = f"Name: {name_match.group(1)}"
            if entry not in db_facts:
                db_facts.append(entry)
                memory_data["facts"] = db_facts
                save_memory(memory_data)
                
        return {"reply": reply}
        
    except Exception as e:
        print(f"AI/Tool Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)