from typing import Optional
from datetime import datetime
from io import StringIO
from .models import DailyPlan


def export_plan_to_ics(plan: DailyPlan) -> str:
    out = StringIO()
    out.write("BEGIN:VCALENDAR\n")
    out.write("VERSION:2.0\n")
    out.write("PRODID:-//Manager//AI Task Manager//EN\n")
    for item in plan.items:
        out.write("BEGIN:VEVENT\n")
        out.write(f"SUMMARY:{item.title}\n")
        out.write(f"DTSTART:{item.start.strftime('%Y%m%dT%H%M%S')}\n")
        out.write(f"DTEND:{item.end.strftime('%Y%m%dT%H%M%S')}\n")
        out.write("END:VEVENT\n")
    out.write("END:VCALENDAR\n")
    return out.getvalue()


def google_calendar_sync_stub(plan: DailyPlan) -> str:
    # Placeholder for Google Calendar sync
    return "Google Calendar sync is not configured in this demo."
