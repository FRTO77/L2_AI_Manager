from datetime import datetime, time
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    due: Optional[datetime] = None
    estimated_minutes: Optional[int] = Field(None, ge=1)
    priority: Optional[int] = Field(3, ge=1, le=5)


class Task(TaskCreate):
    id: str
    created_at: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None


class PlanItem(BaseModel):
    task_id: str
    title: str
    start: datetime
    end: datetime


class DailyPlan(BaseModel):
    date: datetime
    items: List[PlanItem] = []
