from pathlib import Path

ENV_CONTENT = """
# Optional LLM
OPENAI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=OpenAI
OPENAI_MODEL=gpt-4o-mini
OLLAMA_MODEL=llama3:8b-instruct
AI_TEMPERATURE=0.3

# Server
PORT=8001

# Timezone and working hours for planning
TIMEZONE=UTC
WORK_START=09:00
WORK_END=18:00

# Reminders
REMINDER_CHECK_SECONDS=30
""".strip() + "\n"

def main():
    here = Path(__file__).resolve().parent
    env_path = here / ".env"
    example_path = here / ".env.example"
    alt_example = here / "env.example.txt"

    # Write .env if missing
    if not env_path.exists():
        env_path.write_text(ENV_CONTENT, encoding="utf-8")
        print(f"Created {env_path.name}")
    else:
        print(f"Skipped: {env_path.name} already exists")

    # Try to write .env.example; if blocked in tooling, user still gets alt file
    try:
        example_path.write_text(ENV_CONTENT, encoding="utf-8")
        print(f"Created {example_path.name}")
    except Exception as e:
        print(f"Could not write .env.example: {e}")

    alt_example.write_text(ENV_CONTENT, encoding="utf-8")
    print(f"Created {alt_example.name}")

if __name__ == "__main__":
    main()
