from datetime import datetime, timedelta, time
from typing import List
from .models import Task, DailyPlan, PlanItem


def parse_hhmm(s: str) -> time:
    hh, mm = s.split(":")
    return time(int(hh), int(mm))


def heuristic_plan(tasks: List[Task], work_start: str, work_end: str) -> DailyPlan:
    today = datetime.now().date()
    start_t = parse_hhmm(work_start)
    end_t = parse_hhmm(work_end)

    current = datetime.combine(today, start_t)
    end_dt = datetime.combine(today, end_t)

    # Sort by priority asc (1 highest), then due soonest, then estimate desc
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            t.priority if t.priority is not None else 3,
            t.due or datetime.max,
            -(t.estimated_minutes or 30),
        ),
    )

    items: List[PlanItem] = []
    for t in tasks_sorted:
        if t.completed:
            continue
        est = max(15, (t.estimated_minutes or 30))
        start = current
        end = start + timedelta(minutes=est)
        if end > end_dt:
            break
        items.append(PlanItem(task_id=t.id, title=t.title, start=start, end=end))
        current = end

    return DailyPlan(date=datetime.combine(today, time(0, 0)), items=items)
