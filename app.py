import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from Manager.models import TaskCreate, Task, DailyPlan
import Manager.storage as storage
from Manager.planner import heuristic_plan
from Manager.llm import generate_daily_plan_text
from Manager.calendar import export_plan_to_ics, google_calendar_sync_stub
from Manager.scheduler import start_scheduler

load_dotenv()

app = FastAPI(title="Manager — AI Task Manager")
_scheduler = None


@app.on_event("startup")
async def on_startup():
    global _scheduler
    _scheduler = start_scheduler()


# Tasks
@app.get("/tasks", response_model=List[Task])
async def list_tasks():
    return storage.list_tasks()


@app.post("/tasks", response_model=Task)
async def create_task(payload: TaskCreate):
    now = datetime.utcnow()
    task = Task(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description,
        due=payload.due,
        estimated_minutes=payload.estimated_minutes,
        priority=payload.priority,
        created_at=now,
        completed=False,
        completed_at=None,
    )
    return storage.add_task(task)


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, payload: TaskCreate):
    existing = storage.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = Task(
        **existing.model_dump(),
        title=payload.title,
        description=payload.description,
        due=payload.due,
        estimated_minutes=payload.estimated_minutes,
        priority=payload.priority,
    )
    res = storage.update_task(updated)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to update")
    return res


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    ok = storage.delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


@app.post("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(task_id: str):
    existing = storage.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    if existing.completed:
        return existing
    existing.completed = True
    existing.completed_at = datetime.utcnow()
    res = storage.update_task(existing)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to save completion")
    return res


# Planning
@app.post("/plan/generate", response_model=DailyPlan)
async def generate_plan():
    tasks = storage.list_tasks()
    work_start = os.getenv("WORK_START", "09:00")
    work_end = os.getenv("WORK_END", "18:00")

    # Try LLM first
    provider = os.getenv("LLM_PROVIDER", "OpenAI")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct")
    temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))

    plan_text = generate_daily_plan_text(
        [t.model_dump() for t in tasks], work_start, work_end, provider, openai_model, ollama_model, temperature
    )

    if plan_text:
        # For demo, still build heuristic schedule to return structured plan
        plan = heuristic_plan(tasks, work_start, work_end)
        storage.save_plan(plan)
        return plan

    plan = heuristic_plan(tasks, work_start, work_end)
    storage.save_plan(plan)
    return plan


@app.get("/plan/today", response_model=DailyPlan)
async def get_today_plan():
    plan = storage.load_plan()
    if not plan:
        raise HTTPException(status_code=404, detail="No plan generated")
    return plan


# Calendar
@app.get("/calendar/ics", response_class=PlainTextResponse)
async def calendar_ics():
    plan = storage.load_plan()
    if not plan:
        raise HTTPException(status_code=404, detail="No plan to export")
    return export_plan_to_ics(plan)


@app.post("/calendar/google/sync")
async def calendar_google_sync():
    plan = storage.load_plan()
    if not plan:
        raise HTTPException(status_code=404, detail="No plan to sync")
    return {"message": google_calendar_sync_stub(plan)}
