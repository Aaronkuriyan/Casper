# 🧠 CASPER (Cognitive Autonomous System - Personal Edition)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2.svg?logo=google)](https://aistudio.google.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?logo=supabase)](https://supabase.com/)
[![Live Demo](https://img.shields.io/badge/Status-Live-success.svg)](https://casper-seven.vercel.app)

> **Live Application:** [casper-seven.vercel.app](https://casper-seven.vercel.app)

CASPER is a custom-built, full-stack personal AI agent. Unlike standard chatbots, CASPER is designed with persistent state memory and real-world execution capabilities (Function Calling), allowing it to remember user facts across sessions and interact with live external APIs.

---

## 🚀 System Architecture

The system is decoupled into a lightweight frontend client and a heavy-lifting Python backend, communicating via RESTful API.

* **Brain:** Google GenAI (`gemini-2.5-flash`)
* **Backend Framework:** FastAPI (Hosted on Render)
* **Permanent Memory:** Supabase / PostgreSQL (Cloud Database)
* **Frontend Interface:** Vanilla JS / HTML / CSS (Hosted on Vercel)
* **External Integrations:** OpenWeatherMap API (Real-time Tool Calling)

## ✨ Core Capabilities

* **🧠 Persistent Memory State:** Utilizes a PostgreSQL database to securely store and retrieve user facts, names, and preferences, allowing context to persist indefinitely across server restarts.
* **🛠️ Autonomous Tool Execution:** Implements native Function Calling. The AI can dynamically decide when to execute backend Python functions (e.g., fetching live weather data) before formulating a response to the user.
* **⚡ Asynchronous Processing:** Built on ASGI architecture using FastAPI and Uvicorn, ensuring high-throughput and non-blocking API requests.
* **🛡️ Secure Environment:** Complete separation of concerns with strict CORS policies and secure injection of all API keys via environment variables.

---

🔮 Future Roadmap
[x] Integrate cloud database for permanent memory.

[x] Implement real-time tool calling (Weather API).

[ ] Implement Web Speech API for bi-directional voice interaction.

[ ] Add advanced web-scraping tools for live news fetching.

[ ] Migrate frontend to React.js for enhanced component state management.

