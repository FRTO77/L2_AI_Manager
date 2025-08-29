import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel
from .models import Task, TaskCreate, DailyPlan

STORAGE_DIR = Path(__file__).resolve().parent / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
TASKS_FILE = STORAGE_DIR / "tasks.json"
PLAN_FILE = STORAGE_DIR / "plan.json"


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # Corrupted or empty file; recover with default
        return default


def _write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_tasks() -> List[Task]:
    data = _read_json(TASKS_FILE, [])
    return [Task(**t) for t in data]


def save_tasks(tasks: List[Task]) -> None:
    # Use JSON mode to serialize datetime fields to ISO strings
    _write_json(TASKS_FILE, [t.model_dump(mode="json") for t in tasks])


def add_task(new_task: Task) -> Task:
    tasks = list_tasks()
    tasks.append(new_task)
    save_tasks(tasks)
    return new_task


def get_task(task_id: str) -> Optional[Task]:
    for t in list_tasks():
        if t.id == task_id:
            return t
    return None


def update_task(updated: Task) -> Optional[Task]:
    tasks = list_tasks()
    for i, t in enumerate(tasks):
        if t.id == updated.id:
            tasks[i] = updated
            save_tasks(tasks)
            return updated
    return None


def delete_task(task_id: str) -> bool:
    tasks = list_tasks()
    ntasks = [t for t in tasks if t.id != task_id]
    if len(ntasks) == len(tasks):
        return False
    save_tasks(ntasks)
    return True


def save_plan(plan: DailyPlan) -> None:
    # Use JSON mode to serialize datetime fields to ISO strings
    _write_json(PLAN_FILE, plan.model_dump(mode="json"))


def load_plan() -> Optional[DailyPlan]:
    data = _read_json(PLAN_FILE, None)
    if not data:
        return None
    return DailyPlan(**data)
