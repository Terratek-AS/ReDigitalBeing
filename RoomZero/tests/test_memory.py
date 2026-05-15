from pathlib import Path

from app.memory import MemoryStore
from app.models import MemoryItem


def test_add_and_retrieve_memory(tmp_path: Path) -> None:
    episodic = tmp_path / "episodic.json"
    semantic = tmp_path / "semantic.json"
    procedural = tmp_path / "procedural.json"

    store = MemoryStore(episodic, semantic, procedural)

    item = MemoryItem(
        category="episodic",
        content="User likes systems architecture.",
        importance=0.8,
        tags=["preference", "architecture"],
        source="user",
    )
    store.add_memory(item)

    recent = store.get_recent(limit=5)
    assert len(recent) == 1
    assert recent[0].content == "User likes systems architecture."
    assert recent[0].importance == 0.8


def test_retrieve_by_tags(tmp_path: Path) -> None:
    episodic = tmp_path / "episodic.json"
    semantic = tmp_path / "semantic.json"
    procedural = tmp_path / "procedural.json"

    store = MemoryStore(episodic, semantic, procedural)
    store.add_memory(
        MemoryItem(
            category="semantic",
            content="Project name is RoomZero.",
            importance=0.9,
            tags=["project", "name"],
            source="system",
        )
    )
    store.add_memory(
        MemoryItem(
            category="semantic",
            content="Entity name is Eir.",
            importance=0.7,
            tags=["entity"],
            source="system",
        )
    )

    found = store.retrieve_by_tags(["project"])
    assert len(found) == 1
    assert "RoomZero" in found[0].content
