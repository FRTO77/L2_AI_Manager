import requests
import streamlit as st
from datetime import datetime, date, time

st.set_page_config(page_title="Manager Dashboard", page_icon="🗓️", layout="wide")

if "api_base" not in st.session_state:
    st.session_state.api_base = "http://localhost:8001"
if "ics_data" not in st.session_state:
    st.session_state.ics_data = None


def api_get(path: str):
    url = f"{st.session_state.api_base}{path}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def api_post(path: str, json_data=None):
    url = f"{st.session_state.api_base}{path}"
    r = requests.post(url, json=json_data, timeout=15)
    r.raise_for_status()
    return r.json() if r.text else None


def api_put(path: str, json_data=None):
    url = f"{st.session_state.api_base}{path}"
    r = requests.put(url, json=json_data, timeout=15)
    r.raise_for_status()
    return r.json()


def api_delete(path: str):
    url = f"{st.session_state.api_base}{path}"
    r = requests.delete(url, timeout=10)
    r.raise_for_status()
    return r.json()


st.sidebar.header("Settings")
st.session_state.api_base = st.sidebar.text_input("API Base URL", st.session_state.api_base)

st.title("🗓️ Manager — Dashboard")

# Create Task
st.subheader("Create Task")
title = st.text_input("Title")
desc = st.text_area("Description", "")
due_d = st.date_input("Due date", value=None)
due_t = st.time_input("Due time", value=time(17, 0))
est = st.number_input("Estimate (minutes)", min_value=1, max_value=480, value=30)
prio = st.select_slider("Priority (1 high - 5 low)", options=[1,2,3,4,5], value=3)
if st.button("Create", type="primary"):
    due_iso = None
    if due_d:
        d = due_d if isinstance(due_d, date) else date.today()
        t = due_t if isinstance(due_t, time) else time(17,0)
        due_iso = datetime.combine(d, t).isoformat()
    try:
        api_post("/tasks", {
            "title": title,
            "description": desc or None,
            "due": due_iso,
            "estimated_minutes": int(est),
            "priority": int(prio),
        })
        st.success("Task created")
    except Exception as e:
        st.error(f"Create failed: {e}")

st.divider()

# Tasks List
st.subheader("Tasks")
try:
    tasks = api_get("/tasks")
except Exception as e:
    tasks = []
    st.error(f"Load tasks failed: {e}")

for t in tasks:
    cols = st.columns([4,2,1,1,2])
    with cols[0]:
        st.write(f"**{t['title']}**\n\n{t.get('description') or ''}")
    with cols[1]:
        st.caption(f"Due: {t.get('due') or '—'}")
    with cols[2]:
        st.caption(f"Prio: {t.get('priority')}")
    with cols[3]:
        st.caption("✅" if t.get('completed') else "⬜️")
    with cols[4]:
        c1, c2 = st.columns(2)
        if c1.button("Complete", key=f"done_{t['id']}"):
            try:
                api_post(f"/tasks/{t['id']}/complete")
                st.rerun()
            except Exception as e:
                st.error(f"Complete failed: {e}")
        if c2.button("Delete", key=f"del_{t['id']}"):
            try:
                api_delete(f"/tasks/{t['id']}")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")

st.divider()

# Plan
st.subheader("Plan")
c1, c2, c3 = st.columns([1,1,2])
with c1:
    if st.button("Generate Plan", type="primary"):
        try:
            api_post("/plan/generate")
            st.success("Plan generated")
        except Exception as e:
            st.error(f"Generate failed: {e}")
with c2:
    if st.button("Refresh Plan"):
        st.rerun()

plan = None
try:
    plan = api_get("/plan/today")
except Exception:
    pass

if plan:
    for it in plan.get("items", []):
        st.write(f"{it['start']} — {it['end']}  —  {it['title']}")
    try:
        ics_text = requests.get(f"{st.session_state.api_base}/calendar/ics", timeout=10)
        ics_text.raise_for_status()
        st.download_button("Download ICS", data=ics_text.text, file_name="plan.ics", mime="text/calendar")
    except Exception:
        pass
else:
    st.caption("No plan yet")
