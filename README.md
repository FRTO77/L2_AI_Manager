# Manager — AI Task Manager

Manager is an AI-powered task manager that creates daily plans, schedules reminders, and tracks completion. Backend is built with FastAPI, with optional LLM planning via LangChain (OpenAI/Ollama). React Native (or any client) can call the REST API.

## Stack
- Python, FastAPI, Uvicorn
- LangChain (OpenAI or Ollama) for planning (optional)
- Simple JSON storage (filesystem)
- In-process reminder scheduler
- ICS export; Google Calendar sync stub

## Quick Start
1) Create venv and install deps:
```bash
pip install -r requirements.txt
```
2) Create `.env` (option A or B):
   - A) Run generator: `python Manager/create_env.py`
   - B) Copy from `env.example.txt` to `Manager/.env`
3) Run API:
```bash
uvicorn Manager.app:app --reload --port 8001
```
Open docs at `http://localhost:8001/docs`.

## Key Endpoints
- POST `/tasks` create, GET `/tasks` list, PUT/DELETE `/tasks/{id}`, POST `/tasks/{id}/complete`
- POST `/plan/generate` generate daily plan, GET `/plan/today`
- GET `/calendar/ics` export plan as ICS
- POST `/calendar/google/sync` (stub)

## Notes
- LLM is optional; without keys, a heuristic planner is used.
- Reminders run in-process; for production use a dedicated scheduler or queue.

## License
MIT
