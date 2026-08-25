from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile

import pytest

# Configure isolated storage before importing the application. Importing app.main
# performs database bootstrap and must never migrate tracked local runtime data.
TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="roomzero-pytest-"))
os.environ["ROOMZERO_DATA_DIR"] = str(TEST_DATA_DIR)
os.environ["ROOMZERO_PLATFORM_DB_PATH"] = str(
    TEST_DATA_DIR / "platform" / "platform.sqlite"
)

from app.config import (  # noqa: E402
    APPROVED_SOURCES_FILE,
    CONVERSATIONS_FILE,
    EPISODIC_FILE,
    INVITES_FILE,
    KNOWLEDGE_BASE_FILE,
    PROCEDURAL_FILE,
    RESEARCH_JOBS_FILE,
    RESEARCH_QUESTIONS_FILE,
    SEMANTIC_FILE,
    SESSION_FEEDBACK_FILE,
    SOURCE_QUEUE_FILE,
    STATE_FILE,
    TESTERS_FILE,
)
from app.main import platform_store  # noqa: E402


MUTABLE_RUNTIME_FILES = (
    APPROVED_SOURCES_FILE,
    CONVERSATIONS_FILE,
    EPISODIC_FILE,
    INVITES_FILE,
    KNOWLEDGE_BASE_FILE,
    PROCEDURAL_FILE,
    RESEARCH_JOBS_FILE,
    RESEARCH_QUESTIONS_FILE,
    SEMANTIC_FILE,
    SESSION_FEEDBACK_FILE,
    SOURCE_QUEUE_FILE,
    STATE_FILE,
    TESTERS_FILE,
    platform_store.db_path,
)


@pytest.fixture(scope="session", autouse=True)
def cleanup_isolated_test_data() -> None:
    yield
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def restore_runtime_data_after_test() -> None:
    """Keep sequential tests isolated inside the temporary data root."""
    snapshots: dict[Path, bytes | None] = {
        path: path.read_bytes() if path.exists() else None for path in MUTABLE_RUNTIME_FILES
    }
    yield
    for path, data in snapshots.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for suffix in ("-journal", "-wal", "-shm"):
            Path(f"{path}{suffix}").unlink(missing_ok=True)
