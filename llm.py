import os
from typing import List, Optional
from datetime import datetime, timedelta, time

try:
    from langchain_openai import ChatOpenAI
except Exception:
    ChatOpenAI = None  # type: ignore

try:
    from langchain_ollama import ChatOllama
except Exception:
    ChatOllama = None  # type: ignore


def make_llm(provider: str, model: str, temperature: float):
    if provider == "OpenAI" and ChatOpenAI is not None and os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=model, temperature=temperature, api_key=os.getenv("OPENAI_API_KEY"))
    if provider == "Ollama" and ChatOllama is not None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model, base_url=base_url, temperature=temperature)
    return None


def generate_daily_plan_text(tasks: List[dict], work_start: str, work_end: str, provider: str, openai_model: str, ollama_model: str, temperature: float) -> Optional[str]:
    llm = make_llm(provider, openai_model if provider == "OpenAI" else ollama_model, temperature)
    if llm is None:
        return None
    prompt = (
        "You are an expert productivity assistant. Given a list of tasks (title, priority, estimate in minutes, due time), "
        "create a well-ordered daily plan with start/end times (HH:MM), fitting between working hours. Group short tasks, "
        "schedule deep work in the morning, and place urgent tasks earlier. Output as bullet list: '- HH:MM-HH:MM — title'.\n\n"
        f"Working hours: {work_start}-{work_end}.\nTasks (JSON): {tasks}"
    )
    try:
        resp = llm.invoke(prompt)
        return getattr(resp, "content", str(resp))
    except Exception as e:
        return f"LLM error: {str(e)}"
