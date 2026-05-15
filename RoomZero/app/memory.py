from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from app.models import MemoryItem


class MemoryStore:
    def __init__(self, episodic_path: Path, semantic_path: Path, procedural_path: Path) -> None:
        self.paths = {
            "episodic": episodic_path,
            "semantic": semantic_path,
            "procedural": procedural_path,
        }
        self.working_memory: list[MemoryItem] = []

    def _load_list(self, path: Path) -> list[MemoryItem]:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("[]", encoding="utf-8")
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            return [MemoryItem.model_validate(item) for item in raw]
        except Exception:
            return []

    def _save_list(self, path: Path, items: Iterable[MemoryItem]) -> None:
        data = [item.model_dump() for item in items]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_memory(self, item: MemoryItem) -> None:
        if item.category == "working":
            self.working_memory.append(item)
            self.working_memory = self.working_memory[-50:]
            return

        if item.category in self.paths:
            current = self._load_list(self.paths[item.category])
            current.append(item)
            self._save_list(self.paths[item.category], current)

    def get_recent(
        self,
        limit: int = 20,
        categories: list[str] | None = None,
        min_importance: float = 0.0,
    ) -> list[MemoryItem]:
        selected = categories or ["working", "episodic", "semantic", "procedural"]
        all_items: list[MemoryItem] = []

        if "working" in selected:
            all_items.extend(self.working_memory)

        for category in ["episodic", "semantic", "procedural"]:
            if category in selected:
                all_items.extend(self._load_list(self.paths[category]))

        filtered = [m for m in all_items if m.importance >= min_importance]
        filtered.sort(key=lambda m: m.timestamp, reverse=True)
        return filtered[:limit]

    def retrieve_by_tags(self, tags: list[str], limit: int = 20) -> list[MemoryItem]:
        tag_set = {t.lower().strip() for t in tags}
        all_items = self.get_recent(limit=500)
        scored: list[tuple[int, MemoryItem]] = []

        for item in all_items:
            item_tags = {t.lower().strip() for t in item.tags}
            overlap = len(tag_set.intersection(item_tags))
            if overlap > 0:
                scored.append((overlap, item))

        scored.sort(key=lambda pair: (pair[0], pair[1].importance), reverse=True)
        return [item for _, item in scored[:limit]]

    def apply_decay_placeholder(self) -> None:
        # Placeholder for future memory decay implementation.
        # In later phases, this can reduce effective importance over time
        # based on timestamp, access frequency, and reinforcement signals.
        return
