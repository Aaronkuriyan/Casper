# Casper — Personal AI Assistant

> *Powered by Claude AI | Voice-first | Always learning*

Casper is a personal AI assistant inspired by Iron Man's JARVIS. Talk to it using your voice, and it talks back. It remembers you across conversations and helps with anything you throw at it.

---

## Features

- Voice input and output — just speak, it listens and responds
- Powered by Claude (Anthropic API)
- Persistent memory — remembers your name, preferences, and tasks
- Python FastAPI backend
- Clean dark UI that runs in your browser

---

## Project Structure

Casper/
├── frontend/
│   └── index.html        # Full UI — voice, chat, styling all in one
├── backend/
│   ├── main.py           # FastAPI server + Claude API integration
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment variables template
├── .gitignore
└── README.md

---

### Set up the backend

cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

Server starts at http://localhost:8000

### 5. Open the frontend
Open `frontend/index.html` with Live Server in VS Code.

---

## Voice Support

| Browser | Voice Input | Voice Output |
|---------|-------------|--------------|
| Chrome  | Yes         | Yes          |
| Edge    | Yes         | Yes          |
| Firefox | No          | Yes          |
| Safari  | Limited     | Yes          |

Use Chrome or Edge for the best experience.

---

## How to use

- Click the **microphone** button and speak
- Casper listens, thinks, and talks back
- Tell it your name — it will remember you
- Ask it anything — general knowledge, planning, ideas
- Type in the text box if you prefer not to use voice
- Toggle voice replies on/off with the button at the bottom

---

## Roadmap

- [ ] Wake word detection — "Hey Casper"
- [ ] Web search for real-time information
- [ ] Task and reminder system
- [ ] Smarter long-term memory
- [ ] Mobile app

---

## Built With

- [Anthropic Claude](https://anthropic.com) — AI brain
- [FastAPI](https://fastapi.tiangolo.com) — Python backend
- Web Speech API — voice input and output
- Vanilla HTML, CSS, JavaScript — frontend

---

## License

MIT — free to use, modify, and build on.