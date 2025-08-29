import os
from datetime import datetime, timedelta
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil.tz import gettz
from .models import Task
from .storage import list_tasks


def _notify(task: Task):
    # For demo, print to console; in real app, send push/telegram/email
    print(f"[REMINDER] {datetime.now().isoformat()} — Task: {task.title}")


def schedule_reminders(scheduler: BackgroundScheduler):
    tz = gettz(os.getenv("TIMEZONE", "UTC"))
    tasks: List[Task] = list_tasks()
    now = datetime.now(tz)
    for t in tasks:
        if t.completed or not t.due:
            continue
        due_dt = t.due
        # schedule 15 minutes before due time
        remind_at = due_dt - timedelta(minutes=15)
        if remind_at > now:
            scheduler.add_job(_notify, 'date', run_date=remind_at, args=[t])


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.start()
    schedule_reminders(scheduler)
    return scheduler
