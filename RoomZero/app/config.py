from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
PERSONA_DIR = DATA_DIR / "persona"
STATE_DIR = DATA_DIR / "state"
MEMORY_DIR = DATA_DIR / "memory"
LOGS_DIR = DATA_DIR / "logs"
TESTERS_DIR = DATA_DIR / "testers"
RESEARCH_DIR = DATA_DIR / "research"
FEEDBACK_DIR = DATA_DIR / "feedback"
SOURCES_DIR = DATA_DIR / "sources"

PERSONA_FILE = PERSONA_DIR / "eir.json"
STATE_FILE = STATE_DIR / "eir_state.json"
EPISODIC_FILE = MEMORY_DIR / "episodic.json"
SEMANTIC_FILE = MEMORY_DIR / "semantic.json"
PROCEDURAL_FILE = MEMORY_DIR / "procedural.json"
CONVERSATIONS_FILE = LOGS_DIR / "conversations.json"

INVITES_FILE = TESTERS_DIR / "invites.json"
TESTERS_FILE = TESTERS_DIR / "testers.json"

RESEARCH_QUESTIONS_FILE = RESEARCH_DIR / "questions.json"
KNOWLEDGE_BASE_FILE = RESEARCH_DIR / "knowledge_base.json"
RESEARCH_JOBS_FILE = RESEARCH_DIR / "research_jobs.json"

SESSION_FEEDBACK_FILE = FEEDBACK_DIR / "session_feedback.json"

SOURCE_QUEUE_FILE = SOURCES_DIR / "source_queue.json"
APPROVED_SOURCES_FILE = SOURCES_DIR / "approved_sources.json"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    debug: bool
    max_recent_memories: int
    max_recent_logs: int


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    debug = os.getenv("ROOMZERO_DEBUG", "true").strip().lower() == "true"
    max_recent_memories = int(os.getenv("ROOMZERO_MAX_RECENT_MEMORIES", "20"))
    max_recent_logs = int(os.getenv("ROOMZERO_MAX_RECENT_LOGS", "50"))

    return Settings(
        openai_api_key=api_key,
        openai_model=model,
        debug=debug,
        max_recent_memories=max_recent_memories,
        max_recent_logs=max_recent_logs,
    )


def ensure_data_dirs() -> None:
    for directory in [
        PERSONA_DIR,
        STATE_DIR,
        MEMORY_DIR,
        LOGS_DIR,
        TESTERS_DIR,
        RESEARCH_DIR,
        FEEDBACK_DIR,
        SOURCES_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
